
# CantinaShop

![CantinaShop Logo](screenshots/course-logo.png)

---

## Introduction

**CantinaShop** is a comprehensive online store developed as the final project for the Python Web 2025 course at SoftUni. It offers a wide range of accessories and focuses on delivering a seamless and user-friendly shopping experience.

This project showcases the application of modern web development techniques and best practices in Python, including:

- Real-time communication using **WebSockets** for live chat between staff and customers  
- Responsive and modular design with **Tailwind CSS**  
- A hybrid **REST/MVC** architecture  
- Use of **Django Template Language (DTL)**  
- Implementation of **asynchronous programming** patterns  
- Extensive **automated testing** (unit and integration tests)  
- Production-ready **deployment**  
- Client-side interactivity through **AJAX** and **fetch API**  

The platform supports essential e-commerce features such as product management, shopping cart functionality, and user registration, making it a fully functional and practical application.

---

## Important Notes

This project **cannot be run immediately after cloning** due to dependencies on external API services like **Cloudinary** for image storage and processing. To run the project locally, you must set up the necessary environment variables with valid API credentials.

### Required Environment Variables (examples):

- `SECRET_KEY` — Django secret key  
- `CLOUDINARY_CLOUD_NAME`  
- `CLOUDINARY_API_KEY`  
- `CLOUDINARY_API_SECRET`  
- Email service provider credentials and PostgreSQL database configurations  

These variables can be loaded via a `.env` file or system environment using the `python-dotenv` library.

### Online Demo

A live demo of the project is available [here](#) *(link to be provided)*

---

## Technology Stack

- Python 3.11 + Django Framework  
- Django Channels & Daphne for asynchronous support  
- Tailwind CSS for styling  
- PostgreSQL as the primary database  
- Cloudinary for image hosting and management  
- WebSockets for real-time features  
- Django REST Framework  
- Django Template Language (DTL) for rendering views  
- Celery for asynchronous task processing  
- Django ORM for database interactions  

---

## Authentication and Account Management

The authentication system in **CantinaShop** is robust and secure, featuring:

- User registration with email confirmation  
- Login and logout functionality  
- Profile editing and account management  
- Email verification using secure tokens  
- Storage of user information and multiple addresses linked to the account  

---

### Registration and Email Confirmation Workflow

1. User submits registration data via `RegistrationForm` which validates the input.  
2. A new user record (`UserModel`) is created with `is_active = False`.  
3. An email with a verification link is sent using `EmailService.send_confirmation_email`.  
4. The verification link contains an encoded user ID (`uidb64`) and a secure token.

#### Example of a verification URL:
```
/activate/NjEyMw/token123/
```

---

### Account Activation Process

When the user clicks the activation link:

1. The `ActivateAccount` view decodes `uidb64` to retrieve the user.  
2. The token is validated with Django’s `default_token_generator`.  
3. Upon successful validation:  
   - The user's account is activated (`is_active = True`).  
   - The user is logged in automatically.  
4. The user is redirected to either an activation success page or an invalid token page.  

---

### Login and Logout

- Login is handled by Django's standard `LoginView`, supporting username/email and password.  
- Logout uses `LogoutView`, redirecting users to the homepage.  
- Logged-in users are prevented from accessing the login page through a custom `ProfileProhibitedMixin`.  

---

### User Profile and Account Management

Authenticated users can manage their personal data and addresses via the `AccountUpdateView`, which allows:

- Updating personal information (name, phone number, profile photo)  
- Adding, editing, and viewing addresses  
- Managing account settings  

Addresses are stored in the `Address` model and linked to the `Account` model, which is in a one-to-one relation with `UserModel`.

---

### Account Deactivation

- Users can deactivate their accounts using `AccountDeactivateView`.  
- This action sets `is_active = False`, effectively disabling the account and logging the user out.  
- User data is preserved in the database for potential reactivation or administrative review.  

---

### User Roles and Permissions

The platform distinguishes two main user groups to manage permissions:

- **Superusers**: Full access with unrestricted CRUD permissions across the entire system.  
- **Administrators**: Limited administrative rights with certain restrictions compared to superusers.

This role-based access control ensures appropriate separation of duties and enhances security.

---

## Data Models Overview

| Model        | Description                                                  |
|--------------|--------------------------------------------------------------|
| `UserModel`  | Custom user model extending `AbstractUser`; includes unique email and chat ban status |
| `Account`    | One-to-one relationship with `UserModel`; holds personal details and main address |
| `Address`    | Stores multiple user addresses linked to an `Account`       |

---

## URL Endpoints

| Path                         | Description                     |
|------------------------------|--------------------------------|
| `/register/`                 | User registration              |
| `/login/`                   | User login                    |
| `/logout/`                  | User logout                   |
| `/activate/<uidb64>/<token>/` | Email account activation       |
| `/email-confirmation-sent/` | Notification after registration|
| `/activation-success/`      | Account activation success     |
| `/activation-invalid/`      | Invalid or expired activation  |
| `/`                         | User profile view and edit    |
| `/deactivate/`              | Account deactivation           |

---

## Security Measures

- All sensitive operations require authentication.  
- Email confirmation is mandatory for account activation.  
- Custom validators ensure usernames and addresses do not contain profanity (`NoProfanityValidator`).  
- Phone numbers are validated with a custom phone validator to ensure correct format.

---

