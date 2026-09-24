import os

from flask import Flask, request, render_template, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()


# ==========================================================
# FLASK
# ==========================================================

app = Flask(__name__)


# ==========================================================
# MYSQL CONFIGURATION
# ==========================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


# ==========================================================
# DATABASE CONNECTION
# ==========================================================

def get_db_connection():

    try:

        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            connection_timeout=10
        )

        print("MYSQL CONNECTION: OK")

        return connection

    except Error as e:

        print()
        print("==========================================")
        print("MYSQL CONNECTION ERROR")
        print("==========================================")
        print(e)
        print()

        return None


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================================
# BUILD BARCODE VARIANTS
# ==========================================================

def build_code_variants(code):

    variants = []

    def add(value):

        if value and value not in variants:

            variants.append(value)


    add(code)


    # ------------------------------------------------------
    # 14 digits -> also try the 13 last digits
    # ------------------------------------------------------

    if len(code) == 14 and code.isdigit():

        add(code[1:])


    # ------------------------------------------------------
    # 13 digits -> also try a leading 0
    # ------------------------------------------------------

    if len(code) == 13 and code.isdigit():

        add("0" + code)


    # ------------------------------------------------------
    # Try without leading zeros
    # ------------------------------------------------------

    stripped = code.lstrip("0")

    if stripped:

        add(stripped)


    return variants


# ==========================================================
# SEARCH PRODUCT
# ==========================================================

@app.route("/search")
def search():

    # ------------------------------------------------------
    # GET BARCODE
    # ------------------------------------------------------

    code = request.args.get("code")


    print()
    print("==========================================")
    print("BARCODE RECEIVED:", code)
    print("==========================================")


    if not code:

        return jsonify({
            "found": False,
            "message": "No barcode received"
        })


    # ------------------------------------------------------
    # CLEAN BARCODE
    # ------------------------------------------------------

    code = str(code).strip()

    code = code.replace(" ", "")
    code = code.replace("\n", "")
    code = code.replace("\r", "")
    code = code.replace("\t", "")


    print("CLEAN BARCODE:", code)


    # ------------------------------------------------------
    # BUILD CANDIDATES
    # ------------------------------------------------------

    candidates = build_code_variants(code)


    print("CANDIDATES TO TRY:", candidates)


    # ------------------------------------------------------
    # CONNECT MYSQL
    # ------------------------------------------------------

    connection = get_db_connection()


    if connection is None:

        return jsonify({
            "found": False,
            "message": "Unable to connect to MySQL database"
        }), 500


    cursor = None


    try:

        cursor = connection.cursor(dictionary=True)


        # ==================================================
        # SQL PLACEHOLDERS
        # ==================================================

        placeholders = ", ".join(
            ["%s"] * len(candidates)
        )


        # ==================================================
        # SEARCH QUERY
        # ==================================================

        query = f"""

        SELECT

            P.id_product,
            P.id_supplier,
            P.id_manufacturer,
            P.id_category_default,
            P.ean13,
            P.reference,
            P.supplier_reference,
            P.quantity,
            P.price,
            P.cache_default_attribute,
            P.active,

            PA.id_product_attribute,
            PA.upc,

            A.id_attribute,

            AL.name AS size_name,

            AGL.name AS attribute_group_name,

            PL.name AS product_name,

            PL.link_rewrite AS product_link_rewrite,

            C.name AS category_name,

            C.link_rewrite AS category_link_rewrite

        FROM cj6yg_product P


        INNER JOIN cj6yg_product_attribute PA

            ON PA.id_product = P.id_product


        INNER JOIN cj6yg_product_attribute_combination PAC

            ON PAC.id_product_attribute =
               PA.id_product_attribute


        INNER JOIN cj6yg_attribute A

            ON A.id_attribute = PAC.id_attribute


        INNER JOIN cj6yg_attribute_lang AL

            ON AL.id_attribute = A.id_attribute

            AND AL.id_lang = 3


        INNER JOIN cj6yg_attribute_group_lang AGL

            ON AGL.id_attribute_group =
               A.id_attribute_group

            AND AGL.id_lang = 3


        INNER JOIN cj6yg_category_lang C

            ON C.id_category =
               P.id_category_default

            AND C.id_shop = 1

            AND C.id_lang = 3


        INNER JOIN cj6yg_product_lang PL

            ON PL.id_product =
               P.id_product

            AND PL.id_shop = 1

            AND PL.id_lang = 3


        WHERE

            CAST(PA.upc AS CHAR) IN ({placeholders})

            OR

            CAST(P.ean13 AS CHAR) IN ({placeholders})

            OR

            CAST(P.reference AS CHAR) IN ({placeholders})

            OR

            CAST(P.supplier_reference AS CHAR) IN ({placeholders})


        LIMIT 1

        """


        # --------------------------------------------------
        # PARAMETERS
        # --------------------------------------------------

        params = (

            candidates
            + candidates
            + candidates
            + candidates

        )


        # --------------------------------------------------
        # EXECUTE
        # --------------------------------------------------

        cursor.execute(
            query,
            params
        )


        product = cursor.fetchone()


        # ==================================================
        # NOT FOUND
        # ==================================================

        if not product:

            print()
            print("==========================================")
            print("PRODUCT NOT FOUND")
            print("==========================================")
            print("BARCODE:", code)
            print("CANDIDATES:", candidates)
            print()

            return jsonify({

                "found": False,

                "message":
                    "Barcode not found",

                "barcode":
                    code

            })


        # ==================================================
        # PRODUCT FOUND
        # ==================================================

        print()
        print("==========================================")
        print("PRODUCT FOUND")
        print("==========================================")

        print(
            "ID PRODUCT:",
            product["id_product"]
        )

        print(
            "ID PRODUCT ATTRIBUTE:",
            product["id_product_attribute"]
        )

        print(
            "UPC:",
            product["upc"]
        )

        print(
            "EAN13:",
            product["ean13"]
        )

        print(
            "REFERENCE:",
            product["reference"]
        )

        print(
            "NAME:",
            product["product_name"]
        )

        print(
            "ATTRIBUTE GROUP:",
            product["attribute_group_name"]
        )

        print(
            "SIZE / POINTURE:",
            product["size_name"]
        )

        print(
            "ID ATTRIBUTE:",
            product["id_attribute"]
        )


        # ==================================================
        # BUILD PRODUCT URL
        # ==================================================

        category_link = str(
            product["category_link_rewrite"] or ""
        ).strip().lower()


        product_link = str(
            product["product_link_rewrite"] or ""
        ).strip()


        product_id = product["id_product"]


        attribute_group = str(
            product["attribute_group_name"] or ""
        ).strip().lower()


        size_name = str(
            product["size_name"] or ""
        ).strip().lower()


        # --------------------------------------------------
        # FORMAT SIZE
        # --------------------------------------------------

        size_name = (

            size_name

            .replace(" ", "_")

            .replace("/", "_")

            .replace(".", "_")

            .replace("-", "_")

        )


        # ==================================================
        # FINAL URL
        # ==================================================

        url = (

            "https://www.tuttosport.com.tn/"

            + category_link

            + "/"

            + str(product_id)

            + "-"

            + str(product["id_product_attribute"])

            + "-"

            + product_link

            + ".html#/"

            + str(product["id_attribute"])

            + "-"

            + attribute_group

            + "-"

            + size_name

        )


        print()
        print("PRODUCT URL:")
        print(url)
        print()


        # ==================================================
        # PRICE
        # ==================================================

        price = product["price"]


        if price is not None:

            price = float(price)


        # ==================================================
        # JSON RESPONSE
        # ==================================================

        return jsonify({

            "found": True,

            "barcode":
                code,

            "id_product":
                product["id_product"],

            "id_product_attribute":
                product["id_product_attribute"],

            "id_attribute":
                product["id_attribute"],

            "article":
                product["reference"],

            "name":
                product["product_name"],

            "category":
                product["category_name"],

            "id_category_default":
                product["id_category_default"],

            "supplier_reference":
                product["supplier_reference"],

            "quantity":
                product["quantity"],

            "price":
                price,

            "cache_default_attribute":
                product["cache_default_attribute"],

            "ean13":
                product["ean13"],

            "upc":
                product["upc"],

            "attribute_group":
                product["attribute_group_name"],

            "size":
                product["size_name"],

            "url":
                url

        })


    # ======================================================
    # MYSQL ERROR
    # ======================================================

    except Error as e:

        print()
        print("==========================================")
        print("MYSQL QUERY ERROR")
        print("==========================================")
        print(e)
        print()

        return jsonify({

            "found": False,

            "message":
                "Database query error",

            "error":
                str(e)

        }), 500


    # ======================================================
    # GENERAL ERROR
    # ======================================================

    except Exception as e:

        print()
        print("==========================================")
        print("GENERAL SERVER ERROR")
        print("==========================================")
        print(e)
        print()

        return jsonify({

            "found": False,

            "message":
                "Server error",

            "error":
                str(e)

        }), 500


    finally:

        if cursor is not None:

            cursor.close()


        if connection is not None:

            connection.close()


# ==========================================================
# RUN SERVER
# ==========================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("TUTTO SPORT BARCODE SCANNER")
    print("==========================================")

    print("Server starting...")

    print("URL: http://127.0.0.1:5000")

    print("==========================================")
    print()


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )