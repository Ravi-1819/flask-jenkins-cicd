# 🚀 Flask CI/CD Pipeline using Jenkins + Docker + GitHub

## 📌 Project Overview
This project demonstrates a complete CI/CD pipeline using Jenkins, Docker, and GitHub Webhooks.

Whenever code is pushed to GitHub, Jenkins automatically:
- Pulls the latest code
- Builds Docker image
- Stops old container
- Deploys new container

---

## 🔄 CI/CD Flow

GitHub → Jenkins → Docker Build → Docker Run → Live Deployment

---

## 🛠 Tech Stack

- Flask (Python)
- Jenkins (Automation Server)
- Docker (Containerization)
- GitHub (Source Control)
- AWS EC2 (Deployment Server)

---

## 🚀 How it works

1. Developer pushes code to GitHub
2. Webhook triggers Jenkins
3. Jenkins builds Docker image
4. Old container is removed
5. New container is deployed
6. Application goes live

---

## 🌐 Live Application

Deployed on AWS EC2 using Jenkins pipeline.

URL:
http://13.126.51.226:5000

---

## 📦 Features

✔ Automated build  
✔ Automated deployment  
✔ Docker containerization  
✔ GitHub integration  
✔ CI/CD pipeline  

---

## 👨‍💻 Author

Ravi Kumar Singh
