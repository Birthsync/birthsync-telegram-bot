table_users = ('CREATE TABLE IF NOT EXISTS users ('
               'id SERIAL PRIMARY KEY NOT NULL, '
               'user_id BIGINT UNIQUE NOT NULL, '
               'username VARCHAR(32), '
               'fullname TEXT NOT NULL, '
               'email VARCHAR(256) UNIQUE, '
               'phone_number VARCHAR(16) UNIQUE, '
               'is_active BOOL NOT NULL, '
               'is_premium BOOL NOT NULL, '
               'is_superuser BOOL NOT NULL, '
               'created_at BIGINT NOT NULL)'
               )

table_user_cards = ('CREATE TABLE IF NOT EXISTS user_cards ('
                    'id SERIAL PRIMARY KEY NOT NULL, '
                    'user_id BIGINT UNIQUE NOT NULL REFERENCES users(user_id), '
                    'first_name VARCHAR(64), '
                    'last_name VARCHAR(64), '
                    'middle_name VARCHAR(64), '
                    'birthdate BIGINT)')

table_contacts = ('CREATE TABLE IF NOT EXISTS contacts ('
                  'id SERIAL PRIMARY KEY NOT NULL, '
                  'user_id BIGINT NOT NULL REFERENCES users(user_id), '
                  'contact_id BIGINT NOT NULL REFERENCES users(user_id), '
                  'UNIQUE (user_id, contact_id))')

table_wishlists = ('CREATE TABLE IF NOT EXISTS wishlists ('
                   'id SERIAL PRIMARY KEY NOT NULL, '
                   'user_id BIGINT NOT NULL REFERENCES users(user_id), '
                   'contact_id BIGINT, '
                   'data TEXT)')

table_user_categories = ('CREATE TABLE IF NOT EXISTS user_categories ('
                         'id SERIAL PRIMARY KEY NOT NULL, '
                         'user_id BIGINT NOT NULL REFERENCES users(user_id), '
                         'name VARCHAR(32) NOT NULL, '
                         'description VARCHAR(256), '
                         'UNIQUE (user_id, name))')
