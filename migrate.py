from argparse import ArgumentParser, Namespace

from psycopg2 import connect
from bcrypt import hashpw, gensalt


def initiate_parser() -> Namespace:
    """Initiates command line argument parser"""
    parser = ArgumentParser(description="Create required tables and fill with example data")
    parser.add_argument("host", help="RDS database host")
    parser.add_argument("username", help="Main user name")
    parser.add_argument("password", help="Main user password")
    return parser.parse_args()


def get_db_connection_params(host: str) -> dict:
    """Create DB connection params based on given host and other values from Terraform tfvars file."""

    with open("terraform.tfvars") as f:
        tf_pairs = [row.strip().split(" = ") for row in f.readlines()]
        tf_settings = {pair[0]: pair[1].strip('"') for pair in tf_pairs}

    params = {
        "host": host,
        "user": tf_settings["db_username"],
        "password": tf_settings["db_password"],
        "database": "postgres",
        "port": "5432",
    }

    return params


def migrate_db(connection_params: dict, username: str, password: str) -> None:
    """Connects to db with given params, recreated DB tables and fills them with sample data."""
    with connect(**connection_params) as conn:
        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS products")
        cur.execute(
            """CREATE TABLE products (
            id serial PRIMARY KEY,
            name VARCHAR ( 100 ) NOT NULL,
            price INTEGER
        )"""
        )
        cur.execute("INSERT INTO products (name, price) VALUES ('Desk', '500')")
        cur.execute("INSERT INTO products (name, price) VALUES ('Chair', '200')")

        cur.execute("DROP TABLE IF EXISTS users")
        cur.execute(
            """CREATE TABLE users (
            id serial PRIMARY KEY,
            name VARCHAR ( 100 ) NOT NULL,
            password BYTEA
        );"""
        )
        user_credentials = (username, hashpw(password.encode(), gensalt(12)))
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s)", user_credentials)


if __name__ == "__main__":
    args = initiate_parser()
    db_connection_params = get_db_connection_params(args.host)
    migrate_db(db_connection_params, args.username, args.password)
