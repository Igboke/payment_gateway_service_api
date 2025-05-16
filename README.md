# Django Payment Processing Module (Hexagonal Architecture)

A Django module for integrating various payment gateways, designed with a clean Hexagonal (Ports and Adapters) Architecture. This architecture promotes separation of concerns, making the core payment logic independent of specific frameworks (like Django) and external services (like payment gateways).

Currently, this module provides an adapter for **FlutterWave** (specifically for bank transfers and webhook handling).

## ✨ Features

* **Hexagonal Architecture (Ports & Adapters):**
  * **Decoupled Core Logic:** The `core_logic.py` contains business rules and orchestrates payment flows, unaware of Django or specific payment gateways.
  * **Clear Interfaces (Ports):** `PaymentGatewayInterface` and `ClientRepositoryInterface` define contracts for external interactions.
  * **Concrete Implementations (Adapters):** `FlutterWaveAdapter` and `DjangoClientRepositoryAdapter` provide specific implementations for these interfaces.
* **Payment Initiation:** Supports initiating payments via integrated gateways (e.g., FlutterWave bank transfer).
* **Webhook Handling:** Designed to process incoming webhook notifications from payment gateways to update transaction statuses.
* **Data Transfer Objects (DTOs):** Ensures clear and consistent data structures between layers.
* **Django REST Framework Integration:** Provides API endpoints for initiating payments and handling webhooks.
* **Extensible:** Easily add support for new payment gateways by creating new adapters.
* **Testable:** The decoupled nature makes unit testing of core logic and adapters more straightforward.

## 🏛️ Architectural Overview

This module follows the **Ports and Adapters (Hexagonal) Architecture**:

1. **Core Logic (`core_logic.py`):**
    * Contains the application's business rules (e.g., `PaymentServiceCore`).
    * It is completely independent of web frameworks, databases, or third-party services.
    * Defines **Ports** (interfaces) through which it communicates with the outside world.

2. **Ports (`payments_ports_and_adapters.py`, `repositories_ports_and_adapters.py`):**
    * **`PaymentGatewayInterface`**: Defines the contract for how the core logic interacts with any payment gateway (e.g., `process_payment`, `handle_webhook`).
    * **`ClientRepositoryInterface`**: Defines the contract for how the core logic interacts with data storage for clients and transactions (e.g., `get_client_by_email`, `create_payment_transaction`).

3. **Adapters (`payments_ports_and_adapters.py`, `repositories_ports_and_adapters.py`):**
    * **Primary/Driving Adapters (Input):**
        * Django views (`views.py`) and serializers (`serializers.py`) adapt incoming HTTP requests to calls on the `services.py` layer, which then interacts with the `PaymentServiceCore`.
    * **Secondary/Driven Adapters (Output):**
        * `FlutterWaveAdapter`: Implements `PaymentGatewayInterface` to interact with the FlutterWave API.
        * `DjangoClientRepositoryAdapter`: Implements `ClientRepositoryInterface` to interact with the Django ORM for data persistence.

4. **Services (`services.py`):**
    * Acts as an application service layer, orchestrating the instantiation of adapters and coordinating calls between the primary adapters (views) and the core logic.

**Flow Example (Initiate Payment):**
`API View` (Django) -> `initiate_payment` (services.py) -> `PaymentServiceCore.initiate_payment` (core_logic.py) -> `FlutterWaveAdapter.process_payment` & `DjangoClientRepositoryAdapter.create_payment_transaction`

## 📋 Prerequisites

* Python (3.8+ recommended)
* Pip & Virtualenv
* Django (4.x+ recommended)
* Django REST Framework
* `requests` library
* `drf-spectacular` (for API schema generation)
* A running database compatible with Django (e.g., PostgreSQL, MySQL, SQLite for development)
* A FlutterWave account with API Secret Key and Bank Transfer Endpoint URL.

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone github.com/Igboke/payment_gateway_service_api.git
cd payment_gateway_service_api
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in your project root (where `manage.py` is typically located) and add your credentials and settings.
**Never commit your `.env` file to version control!** Add `.env` to your `.gitignore` file.

```env
# .env
DEBUG=True
SECRET_KEY='your-django-secret-key' 

FLUTTERWAVE_SECRET_KEY='your_flutterwave_secret_key'
```

Ensure your Django `settings.py` can load these (e.g., using `python-dotenv` or `django-environ`):

```python
# settings.py
import os
from dotenv import load_dotenv

load_dotenv() # Loads variables from .env

# ...
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'


# Custom settings for your payment module
FLUTTERWAVE_SECRET_KEY = os.getenv('FLUTTERWAVE_SECRET_KEY')
# ...
```


### 5. Run the Development Server

```bash
python manage.py runserver
```

The API endpoints should now be accessible, typically under `http://127.0.0.1:8000/api/payments/`.

## ⚙️ API Endpoints

The following endpoints are provided by `views.py` and configured in `urls.py`:

### 1. Initiate Payment

* **Endpoint:** `POST /api/payments/v1/createpayment/`
* **Description:** Initiates a bank transfer payment request via FlutterWave.
* **Request Body (`application/json`):**

    ```json
    {
        "email": "client@example.com",
        "currency": "NGN", // Or other supported currency
        "is_permanent": false // Optional, defaults to false
    }
    ```

* `email` (string, required): Email of the client making the payment.
* `currency` (string, required): Currency code (e.g., "NGN", "USD").
* `is_permanent` (boolean, optional): Indicates if the payment is for a permanent virtual account (FlutterWave specific).
* **Success Response (200 OK):**

    ```json
    {
        "transaction_ref": "your-unique-transaction-ref-uuid",
        "gateway_response": {
            "status": "success",
            "message": "Transfer Queued Successfully",
            "data": { /* ... Flutterwave specific data ... */ },
            "meta": {
                "authorization": {
                    "transfer_reference": "FW-TRANSFER-REF-123",
                    "transfer_account": "0123456789",
                    "transfer_bank": "Access Bank",
                    "account_expiration": "2023-12-31T23:00:00.000Z",
                    "transfer_note": "Please make a bank transfer to this account",
                    "transfer_amount": 5000, // Amount might be here or in request
                    "mode": "test"
                }
            }
        }
    }
    ```

* **Error Responses:**
* `400 Bad Request`: Invalid input data.
* `404 Not Found`: Client or order not found.
* `500 Internal Server Error`: Gateway communication error or other server-side issues.

### 2. Handle Webhook

* **Endpoint:** `POST /api/payments/v1/webhook/`
* **Description:** Receives webhook notifications from the payment gateway (e.g., FlutterWave) to update transaction status.
* **Request Body (`application/json`):**
    The structure of the webhook payload is determined by the payment gateway (e.g., FlutterWave).
    Example (Flutterwave successful transfer):

    ```json
    {
        "event": "charge.completed", 
        "data": {
            "id": 123456,
            "tx_ref": "your-unique-transaction-ref-uuid",
            "flw_ref": "FLW-REF-ABCDEF123456",
            "amount": 5000,
            "currency": "NGN",
            "status": "successful", // or "failed", "pending"
            // ... other Flutterwave specific data ...
        }
    }
    ```

* **Success Response (200 OK):**

    ```json
    // The content of the successful response for a webhook can vary.
    // Often, a simple confirmation is sufficient.
    // Based on update_model_from_webhook, it returns a boolean.
    true
    ```

    Or, if returning a DTO:

    ```json
    {
        "status": "success", // Or "updated"
        "message": "Transaction updated successfully"
    }
    ```

    **Important:** Gateways usually expect a `200 OK` response quickly to acknowledge receipt.
* **Error Responses:**
* `400 Bad Request`: Invalid payload, missing crucial data.
* `404 Not Found`: Transaction corresponding to the webhook not found.

### API Documentation

`drf-spectacular` is configured, you can access auto-generated API documentation at:

* Swagger UI: `http://127.0.0.1:8000/api/schema/swagger-ui/`
* ReDoc: `http://127.0.0.1:8000/api/schema/redoc/`

## 🧪 Running Tests

To run tests for this app (e.g., `payments_app`):

```bash
python manage.py test 
```

Or to run all tests in the project:

```bash
python manage.py test
```

## 📁 Project Structure Overview

* `core_logic.py`: Contains the `PaymentServiceCore` and DTOs used internally by the core.
* `payments_ports_and_adapters.py`:
  * `PaymentGatewayInterface` (Port)
  * `PaymentDetails`, `GatewayProcessPaymentResponseDTO`, `GatewayWebhookEventDTO` (Data contracts for the port)
  * `FlutterWaveAdapter` (Adapter for FlutterWave)
* `repositories_ports_and_adapters.py`:
  * `ClientRepositoryInterface` (Port)
  * `ClientDTO`, `PaymentTransactionDTO`, `CreateTransactionDTO`, `UpdateTransactionDTO` (Data contracts for the port)
  * `DjangoClientRepositoryAdapter` (Adapter for Django ORM)
* `services.py`: Application service layer, orchestrates interactions between views, core logic, and adapters.
* `views.py`: Django REST Framework API views for handling HTTP requests.
* `serializers.py`: Django REST Framework serializers for request/response data validation and transformation.
* `urls.py`: URL routing for the payment API endpoints.
* `models.py` (Implicit, from `Orders.models`, `Products.models` etc.): Django models for `PaymentTransaction`, `Orders`, `ClientModel`, etc.

## 🔧 Extending with New Payment Gateways

One of the key benefits of this architecture is the ease of adding new payment gateways:

1. **Define DTOs (if needed):** If the new gateway has significantly different request/response structures that cannot be mapped to existing DTOs (`PaymentDetails`, `GatewayProcessPaymentResponseDTO`, `GatewayWebhookEventDTO`), define new ones or adapt existing ones.
2. **Create New Adapter:**
    * Create a new class (e.g., `PaystachAdapter`) in `payments_ports_and_adapters.py`.
    * This class must implement the `PaymentGatewayInterface`.
    * Implement the `process_payment`, `handle_webhook`, and `verify_payment` methods, translating data to/from the new gateway's API and your core DTOs.
3. **Update Service Layer (`services.py`):**
    * Modify the `initiate_payment` (and potentially a new `handle_webhook_service`) function in `services.py` to allow selection of the desired gateway adapter. This could be based on a parameter in the request, configuration, or client settings.
    * Instantiate the new adapter when appropriate.
    * Example:

        ```python
        # services.py
        # ...
        from .payments_ports_and_adapters import FlutterWaveAdapter, PayStackAdapter # Import new adapter

        def initiate_payment(validated_data, gateway_name: str) -> Dict[str, Any]:
            client_repo_adapter = DjangoClientRepositoryAdapter()

            if gateway_name == "FlutterWave":
                payment_gateway_adapter = FlutterWaveAdapter()
            elif gateway_name == "Paystack":
                payment_gateway_adapter = PayStackAdapter()
            else:
                raise ValueError(f"Unsupported gateway: {gateway_name}")

            payment_service = PaymentServiceCore(
                gateway_adapter=payment_gateway_adapter,
                client_repository=client_repo_adapter
            )
            # ... rest of the logic
        ```

4. **Update API Layer (`views.py`, `serializers.py`):**
    * If necessary, update serializers to accept gateway selection.
    * Update views to pass the chosen gateway to the service layer.

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute, please:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes.
4. Write tests for your changes.
5. Ensure all tests pass.
6. Commit your changes (`git commit -m 'Add some feature'`).
7. Push to the branch (`git push origin feature/your-feature-name`).
8. Open a Pull Request.

Please ensure your code adheres to any existing coding standards and includes relevant documentation.

## 📜 License
