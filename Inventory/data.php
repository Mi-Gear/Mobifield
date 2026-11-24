<?php
declare(strict_types=1);

/*
 * Mobifield Mini App endpoint.
 * GET /inventory/data                    -> inventory JSON (Telegram initData required)
 * GET /inventory/data?image=item_id      -> WebP image when available, otherwise PNG
 */

$projectRoot = realpath(dirname(__DIR__));
if ($projectRoot === false) {
    http_response_code(500);
    exit('Project directory not found');
}

function jsonResponse(array $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function getDatabase(string $projectRoot): PDO
{
    $databasePath = $projectRoot . '/utils/db.sqlite';
    if (!is_file($databasePath) || !is_readable($databasePath)) {
        throw new RuntimeException('SQLite database is missing or not readable');
    }

    return new PDO('sqlite:' . $databasePath, null, null, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);
}

function getBotToken(string $projectRoot): string
{
    $tokenPath = $projectRoot . '/token.txt';
    if (!is_file($tokenPath) || !is_readable($tokenPath)) {
        throw new RuntimeException('token.txt is missing or not readable by PHP');
    }

    $token = trim((string) file_get_contents($tokenPath));
    if ($token === '') {
        throw new RuntimeException('Telegram bot token is empty');
    }

    return $token;
}

function validateTelegramInitData(string $initData, string $botToken): int
{
    if ($initData === '' || strlen($initData) > 8192) {
        throw new InvalidArgumentException('Telegram initData is missing or invalid');
    }

    parse_str($initData, $values);
    if (!is_array($values) || !isset($values['hash']) || !is_string($values['hash'])) {
        throw new InvalidArgumentException('Telegram initData has no hash');
    }

    $receivedHash = $values['hash'];
    unset($values['hash']);

    foreach ($values as $value) {
        if (!is_string($value)) {
            throw new InvalidArgumentException('Telegram initData contains invalid fields');
        }
    }

    ksort($values, SORT_STRING);
    $parts = [];
    foreach ($values as $key => $value) {
        $parts[] = $key . '=' . $value;
    }
    $dataCheckString = implode("\n", $parts);

    // Telegram Web Apps validation: HMAC key is the literal "WebAppData".
    $secretKey = hash_hmac('sha256', $botToken, 'WebAppData', true);
    $expectedHash = hash_hmac('sha256', $dataCheckString, $secretKey);

    if (!hash_equals($expectedHash, $receivedHash)) {
        throw new InvalidArgumentException('Telegram initData signature is invalid');
    }

    $authDate = isset($values['auth_date']) ? (int) $values['auth_date'] : 0;
    $now = time();
    if ($authDate <= 0 || $authDate > $now + 30 || $now - $authDate > 86400) {
        throw new InvalidArgumentException('Telegram initData has expired');
    }

    $userJson = $values['user'] ?? '';
    $user = json_decode($userJson, true);
    if (!is_array($user) || !isset($user['id']) || !is_int($user['id'])) {
        throw new InvalidArgumentException('Telegram user ID is missing');
    }

    return $user['id'];
}

function preferredImagePath(string $pngPath): string
{
    $webpPath = preg_replace('/\.png$/i', '.webp', $pngPath);
    if (is_string($webpPath) && is_file($webpPath) && is_readable($webpPath)) {
        $resolved = realpath($webpPath);
        if ($resolved !== false) {
            return $resolved;
        }
    }

    return $pngPath;
}

function imagePath(PDO $db, string $projectRoot, string $imageId): string
{
    $placeholder = $projectRoot . '/images/placeholder.png';

    if ($imageId === '__placeholder__') {
        $path = realpath($placeholder);
        if ($path === false || !is_file($path)) {
            throw new RuntimeException('Placeholder image not found');
        }
        return preferredImagePath($path);
    }

    if (!preg_match('/^[a-z0-9_-]{1,100}$/D', $imageId)) {
        throw new InvalidArgumentException('Invalid image ID');
    }

    $statement = $db->prepare('SELECT image_pathname FROM item_base WHERE id = :id LIMIT 1');
    $statement->execute([':id' => $imageId]);
    $item = $statement->fetch();

    if ($item && !empty($item['image_pathname'])) {
        $relativeDirectory = trim((string) $item['image_pathname'], '/');
        $candidate = realpath($projectRoot . '/' . $relativeDirectory . '/' . $imageId . '.png');
        $rootPrefix = rtrim($projectRoot, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR;

        if (
            $candidate !== false
            && strpos($candidate, $rootPrefix) === 0
            && is_file($candidate)
            && is_readable($candidate)
        ) {
            return preferredImagePath($candidate);
        }
    }

    $fallback = realpath($placeholder);
    if ($fallback === false || !is_file($fallback) || !is_readable($fallback)) {
        throw new RuntimeException('Item image and placeholder image are unavailable');
    }

    return preferredImagePath($fallback);
}

try {
    // Images are static game artwork and can be requested directly by the browser.
    if (isset($_GET['image'])) {
        $db = getDatabase($projectRoot);
        $path = imagePath($db, $projectRoot, (string) $_GET['image']);

        $isWebp = strtolower(pathinfo($path, PATHINFO_EXTENSION)) === 'webp';
        $contentType = $isWebp ? 'image/webp' : 'image/png';
        $fileSize = filesize($path);
        $etag = '"' . dechex((int) filemtime($path)) . '-' . dechex((int) $fileSize) . '"';

        header('Content-Type: ' . $contentType);
        header('Content-Length: ' . (string) $fileSize);
        header('Cache-Control: public, max-age=2592000');
        header('ETag: ' . $etag);
        header('X-Content-Type-Options: nosniff');

        if (trim((string) ($_SERVER['HTTP_IF_NONE_MATCH'] ?? '')) === $etag) {
            http_response_code(304);
            exit;
        }

        readfile($path);
        exit;
    }

    $headers = function_exists('getallheaders') ? getallheaders() : [];
    $initData = $headers['X-Telegram-Init-Data']
        ?? $headers['x-telegram-init-data']
        ?? ($_SERVER['HTTP_X_TELEGRAM_INIT_DATA'] ?? '');

    $playerId = validateTelegramInitData((string) $initData, getBotToken($projectRoot));
    $db = getDatabase($projectRoot);

    $playerStatement = $db->prepare('SELECT gold FROM players WHERE ID = :id LIMIT 1');
    $playerStatement->execute([':id' => $playerId]);
    $player = $playerStatement->fetch();

    if (!$player) {
        jsonResponse(['error' => 'Персонаж не найден'], 404);
    }

    $itemsStatement = $db->prepare(
        'SELECT
            item_base.id,
            item_base.name,
            inventory.count,
            item_base.location,
            item_base.type,
            item_base.rarity,
            item_base.cost,
            item_base.description
         FROM inventory
         INNER JOIN item_base ON item_base.id = inventory.id
         WHERE inventory.pl_id = :player_id'
    );
    $itemsStatement->execute([':player_id' => $playerId]);

    $items = [];
    foreach ($itemsStatement->fetchAll() as $item) {
        $items[] = [
            'id' => (string) $item['id'],
            'name' => $item['name'],
            'count' => (int) $item['count'],
            'location' => (string) $item['location'],
            'type' => $item['type'],
            'rarity' => $item['rarity'],
            'cost' => $item['cost'] === null ? null : (int) $item['cost'],
            'description' => $item['description'],
            'image' => '/inventory/data?image=' . rawurlencode((string) $item['id']),
        ];
    }

    jsonResponse([
        'items' => $items,
        'gold' => (int) $player['gold'],
    ]);
} catch (InvalidArgumentException $error) {
    jsonResponse(['error' => $error->getMessage()], 401);
} catch (Throwable $error) {
    error_log('[Mobifield PHP inventory] ' . $error->getMessage());
    jsonResponse(['error' => 'Ошибка PHP API. Подробности записаны в журнал сервера.'], 500);
}
