from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Database Connection
conn = mysql.connector.connect(
    host="mysql-4a991a1-abarakadabara698-7bd8.c.aivencloud.com",
    user="avnadmin",
    password="AVNS_Rfu9thyCzg-r-9CcyXE",
    database="defaultdb",
    port=10038
)
cursor = conn.cursor(dictionary=True)

# Create User
@app.route("/user", methods=["POST"])
def create_user():
    data = request.json
    try:
        # Insert into Users table
        sql_users = """
            INSERT INTO Users (PersonID, FullName, Email, Password, PhoneNumber) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql_users, (data["PersonID"], data["FullName"], data["Email"], data["Password"], data["PhoneNumber"]))

        # Insert into User_Organizations table
        sql_organizations = """
            INSERT INTO User_Organizations (UserID, OrganizationID) 
            VALUES (%s, %s)
        """
        cursor.execute(sql_organizations, (data["PersonID"], data["OrganizationID"]))

        # Insert into TrustedContacts table
        sql_trusted_contacts = """
            INSERT INTO TrustedContacts (UserID, TrustedContactID, TrustedContactName, TrustedContactNumber) 
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(sql_trusted_contacts, (data["PersonID"], data["TrustedContactID"], data["TrustedContactName"], data["TrustedContactNumber"]))

        conn.commit()
        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# Update Trusted Contact
@app.route("/updateTrustedContactNumber/<email>", methods=["PUT"])
def update_trusted_contact_number(email):
    data = request.json
    try:
        sql = """
            UPDATE TrustedContacts 
            SET TrustedContactName = %s, TrustedContactNumber = %s 
            WHERE UserID = (SELECT PersonID FROM Users WHERE Email = %s)
        """
        cursor.execute(sql, (data["TrustedContactName"], data["TrustedContactNumber"], email))
        conn.commit()
        return jsonify({"message": "Trusted Contact updated successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# Read User
@app.route("/user/<int:person_id>", methods=["GET"])
def get_user(person_id):
    cursor.execute("SELECT * FROM UserData WHERE PersonID = %s", (person_id,))
    user = cursor.fetchone()
    return jsonify(user) if user else (jsonify({"error": "User not found"}), 404)

# Update User
@app.route("/user/<int:person_id>", methods=["PUT"])
def update_user(person_id):
    data = request.json
    try:
        sql = """
            UPDATE Users 
            SET FullName = %s, Email = %s, PhoneNumber = %s 
            WHERE PersonID = %s
        """
        cursor.execute(sql, (data["FullName"], data["Email"], data["PhoneNumber"], person_id))
        conn.commit()
        return jsonify({"message": "User updated successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# Delete User
@app.route("/user/<int:person_id>", methods=["DELETE"])
def delete_user(person_id):
    try:
        cursor.execute("DELETE FROM TrustedContacts WHERE UserID = %s", (person_id,))
        cursor.execute("DELETE FROM User_Organizations WHERE UserID = %s", (person_id,))
        cursor.execute("DELETE FROM Users WHERE PersonID = %s", (person_id,))

        conn.commit()
        return jsonify({"message": "User deleted successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

# Get all emails for an organization
@app.route("/organization/<org_name>/emails", methods=["GET"])
def get_emails_by_org(org_name):
    cursor.execute("SELECT Email FROM UserData WHERE Organization = %s", (org_name,))
    emails = cursor.fetchall()
    return jsonify(emails)

# Get all user data for an organization
@app.route("/organization/<org_name>/users", methods=["GET"])
def get_users_by_org(org_name):
    cursor.execute("SELECT * FROM UserData WHERE Organization = %s", (org_name,))
    users = cursor.fetchall()
    return jsonify(users)

# Get user data based on emails
@app.route("/users/by-email", methods=["POST"])
def get_users_by_emails():
    data = request.json
    emails = tuple(data["emails"])
    if not emails:
        return jsonify({"error": "No emails provided"}), 400

    sql = f"SELECT * FROM UserData WHERE Email IN ({','.join(['%s'] * len(emails))})"
    cursor.execute(sql, emails)
    users = cursor.fetchall()
    return jsonify(users)

@app.route("/users/verify-user", methods=["POST"])
def verify_user():
    data = request.json
    email = data["email"]
    password = data["password"]

    cursor.execute("SELECT * FROM Users WHERE Email = %s", (email,))
    user = cursor.fetchone()

    if user:
        if user["Password"] == password:
            return jsonify({"status": "verified", "user_data": user}), 200
        else:
            return jsonify({"status": "password_wrong"}), 401
    else:
        return jsonify({"status": "user_not_found"}), 404

# Get all users
@app.route("/allusers", methods=["GET"])
def get_all_users():
    cursor.execute("SELECT * FROM UserData ")
    users = cursor.fetchall()
    return jsonify(users)

if __name__ == "__main__":
    app.run(debug=True)
