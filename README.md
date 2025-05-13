
# Expense Tracker ✅

![image](https://github.com/user-attachments/assets/2643c08b-b4b9-4eb6-9609-2e7d44e9b2eb)
![image](https://github.com/user-attachments/assets/ecaf66d8-c28b-45da-bdb1-fe761e589d34)
![image](https://github.com/user-attachments/assets/62a6728b-9a3c-4d83-8b5e-8ef88e87f7da)
![image](https://github.com/user-attachments/assets/b0d4be87-2f0d-48a7-a3a2-12b9b851e728)
![image](https://github.com/user-attachments/assets/a2859510-0985-47a3-9b70-6b4ee1e673b1)
![image](https://github.com/user-attachments/assets/929b1438-388e-4f18-a4e8-96525a038aba)
![image](https://github.com/user-attachments/assets/90985f35-10e9-4bf4-9ea6-d65da8919693)
![image](https://github.com/user-attachments/assets/5658b792-8bbd-4ea0-a8ad-a91435846071)
![image](https://github.com/user-attachments/assets/01f0612b-5315-4db2-a737-5f91392d6c49)
![image](https://github.com/user-attachments/assets/4196f67d-8265-4bdb-9ab8-96135bb519bf)

A simple and powerful expense tracking web app built with Flask.

🚀 **Features**  
📝 Add, edit, and delete expenses  
✅ Track spending with customizable budgets  
📊 Visualize spending trends with weekly and monthly charts (Matplotlib)  
🔒 Secure user authentication (login/signup)  
🌍 User settings for preferred currency and budget reset schedules  
🎨 Responsive UI with Bootstrap, featuring dashboards and budget progress bars  

📂 **Project Structure**  
```
expense_tracker/  
│── app/  
│   ├── __init__.py      # Flask app setup  
│   ├── models.py        # Database models (User, Expense, Budget, etc.)  
│   ├── routes/  
│   │   ├── auth.py      # Authentication routes  
│   │   ├── dashboard.py # Dashboard and spending charts  
│   │   ├── expenses.py  # Expense and budget management  
│   │   ├── settings.py  # User and budget settings  
│   ├── templates/       # HTML templates (dashboard, expenses, settings, etc.)  
│   ├── static/         # CSS, JS, and images  
│── db.sqlite3           # SQLite database  
│── requirements.txt     # Dependencies  
```

⚙️ **Installation & Setup**  
1️⃣ Clone the repository  
```bash
git clone https://github.com/yourusername/expense_tracker.git
cd expense_tracker
```

2️⃣ Install dependencies  
```bash
pip install -r requirements.txt
```

3️⃣ Run the app  
```bash
python -m flask run
```

🛠️ **Technologies Used**  
- **Backend**: Flask, Python  
- **Frontend**: HTML, CSS, JavaScript, Bootstrap  
- **Database**: SQLite, Flask-SQLAlchemy  
- **Additional Features**:  
  - 📊 **Matplotlib** for spending visualizations  
  - 🔒 **Flask-Login** for secure authentication  
  - ⚙️ **Flask-Migrate** for database migrations  



 
