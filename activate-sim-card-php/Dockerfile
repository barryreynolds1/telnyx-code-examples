FROM php:8.3-cli

WORKDIR /app

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

COPY composer.json composer.lock* ./
RUN composer install --no-dev --no-interaction --optimize-autoloader

COPY . .

RUN useradd -r appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["php", "-S", "0.0.0.0:8000", "-t", "public", "index.php"]
