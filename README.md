# CantinaShop

![CantinaShop Logo](screenshots/course-logo.png)

## Introduction

**CantinaShop** is an online store created as a final project for Python Web 2025 at SoftUni. The store offers a variety of accessories, aiming to provide users with an easy and convenient shopping experience.

The project demonstrates the use of modern web technologies and best practices in web application development with Python, including:

- **Web Sockets** for live chat between staff and users  
- Styling with **Tailwind CSS**  
- Hybrid **REST/MVC** architecture  
- Use of **Django Template Language (DTL)**  
- **Asynchronous programming**  
- **Automated tests (unit and integration)**  
- The project is successfully **deployed** and accessible in production  
- **AJAX** and **fetch API** for client-side requests  

Included functionalities cover product management, shopping cart, and user registration, making the application complete and practical for use.

---

## Important

This project **cannot be run directly after cloning**, since it uses configurations for external API services, such as **Cloudinary** for image storage and processing. To run locally, you must configure the required environment variables and provide valid API keys.

### Required configurations (example):

- `SECRET_KEY` — Django secret key  
- `CLOUDINARY_CLOUD_NAME`  
- `CLOUDINARY_API_KEY`  
- `CLOUDINARY_API_SECRET`  
- Email Service Provider and PostgreSQL configurations  

These variables are loaded from a `.env` file or system environment using the `python-dotenv` library.

### Online demo

You can check the live project here: The link to the project will be provided here

---

## Tools used

- Python 3.11 + Django  
- Django Channels & Daphne  
- Tailwind CSS  
- PostgreSQL  
- Cloudinary image hosting  
- WebSockets  
- Django Rest Framework  
- DTL templates  
- Celery  
- Django ORM  
---

## 🔐 Authentication and Account Management

The authentication and account management system in **CantinaShop** includes:

- ✅ Registration with email confirmation  
- 🔓 Login and logout  
- 👤 Profile editing and account deactivation  
- 📧 Verification through token and secure link  
- 🧱 Account information + addresses linked to the user  

---

### 📝 Registration and email confirmation

When a user registers:

1. Data is validated via `RegistrationForm`.  
2. A user (model `UserModel`) is created with `is_active = False`.  
3. A verification link is sent via email through `EmailService.send_confirmation_email`.  
4. The link contains `uidb64` (encoded user ID) and a secure `token`.  

#### Sample email link:
```
/activate/NjEyMw/token123/
```

---

### ✅ Account activation

When the user clicks the link:

1. The `ActivateAccount` view decodes `uidb64` and retrieves the user.  
2. The token is checked using `default_token_generator`.  
3. If valid:  
   - The account becomes active (`is_active = True`)  
   - The user is logged in automatically  
4. Redirect to `activation_success` or `activation_invalid`  

---

### 🔓 Login and logout

- Login uses the standard `LoginView`, with username/email and password.  
- Logout uses `LogoutView`, redirecting to the homepage.  
- Login is blocked for already logged-in users via `ProfileProhibitedMixin`.  

---

### 👤 Profile and editing

Users can manage their information via the `AccountUpdateView`, which allows:

- Changing personal data (name, phone, photo)  
- Adding or editing address (street, city, country, etc.)  
- Viewing current account  

Addresses are stored in the `Address` model, linked to `Account`, which in turn is linked to `UserModel`.

---

### ❌ Account deactivation

- Users can deactivate their profile via `AccountDeactivateView`.  
- This sets `is_active = False`, disables the account, and performs automatic logout.  
- Data is not deleted — the profile remains in the database for possible restoration or administrative handling.  

---

### 👥 User groups and roles

The system has two main groups with different permissions:

- **Superusers** – have full access and CRUD operations over all system resources.  
- **Administrators** – have limited CRUD rights, allowing management of most parts of the app with some restrictions compared to superusers.  

This role-based authorization ensures separation of responsibilities and control over critical operations in the platform.

---

### 📁 Models

| Model        | Description                                                   |
|--------------|---------------------------------------------------------------|
| `UserModel`  | Extension of `AbstractUser` – added unique `email`, `is_chat_banned`, and more |
| `Account`    | Linked 1:1 with `UserModel`. Contains personal data and main address |
| `Address`    | Contains user addresses. Allows multiple addresses per profile |

---

### ⚙️ URL routes

| Path                         | Action                         |
|------------------------------|--------------------------------|
| `/register/`                 | Registration                   |
| `/login/`                   | Login                         |
| `/logout/`                  | Logout                        |
| `/activate/<uidb64>/<token>/` | Account confirmation          |
| `/email-confirmation-sent/` | Email sent notification       |
| `/activation-success/`      | Account activated             |
| `/activation-invalid/`      | Invalid or expired token      |
| `/`                         | Profile view and edit         |
| `/deactivate/`              | Account deactivation          |

---

### 🔒 Security

- All sensitive actions (edit, deactivate) require authentication.  
- Accounts cannot be activated without email confirmation.  
- Validators prevent profanity in usernames and addresses (`NoProfanityValidator`).  
- Phone numbers are validated with a custom validator.
