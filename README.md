# SmartHire-tracker-and-analyzer-

This repository contains the **SmartHire-tracker-and-analyzer-** full-stack application used for managing job applications, resume keyword matching, pipeline analytics charts, and student/admin dashboards.

* **GitHub Link:** [https://github.com/khushiagrawal062003/SmartHire-tracker-and-analyzer-](https://github.com/khushiagrawal062003/SmartHire-tracker-and-analyzer-)
* **Deploy Link:** [https://smarthire-y2ot.onrender.com](https://smarthire-y2ot.onrender.com)

---

## Project Structure

* **smarthire/** - Django project settings, configurations, and core URL routers.
* **tracker/** - Core job application management views, NoSQL queries, reminders timeline, and user dashboard.
* **analyzer/** - Resume parser regular expression engine and matching results page.
* **api/** - REST API views and serialization classes built with Django REST Framework.
* **static/** - Global CSS styling (Light/Dark themes variables) and illustration graphics.
* **templates/** - HTML templates extending the custom glassmorphic layout.

---

## Setup Instructions

### Local Development

1. Navigate to the project root folder:
   ```bash
   cd SmartHire-tracker-and-analyzer-
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Database Setup:
   * Make sure **MongoDB Community Server** is running locally on port `27017`.
   * Apply SQLite migrations for user accounts and session registers:
     ```bash
     python manage.py migrate
     ```

5. Run the server:
   ```bash
   python manage.py runserver
   ```
   * The web application and Django REST APIs will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## Building for Production

* **Frontend:** Compress and collect static files (WhiteNoise setup):
  ```bash
  python manage.py collectstatic --no-input
  ```
* **Backend:** Use a production WSGI server pointing at `smarthire.wsgi:application` (using Gunicorn).

---

## Deployment

The application is deployed as a unified Python Web Service on **Render**, connecting to a cloud-hosted **MongoDB Atlas** cluster. 

* Configure the **`MONGODB_URI`** environment variable in your Render dashboard environment panel to link your MongoDB Atlas cluster.
* Set the **`DJANGO_SECRET_KEY`** and **`DEBUG=False`** variables for production safety.

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Make your changes and commit them with clear messages.
4. Push to your fork and create a pull request.

---

## License

This project is open source.
