# JewelStore Management System  

## 📌 Overview  

**JewelStore Management System** is a jewelry order management solution that streamlines custom jewelry requests, manufacturing cost calculations, and order tracking. It ensures efficient coordination between store managers, factory managers, and customers while providing features like CAD image generation, profit margin adjustments, and order exports.  

---

## 🚀 Features  
✅ **Order Management** – Store managers create orders with customer details and reference images.  
✅ **Manufacturing Cost Calculation** – Factory managers determine production costs (visible only to factory/store managers).  
✅ **Profit Margin Addition** – Store managers apply a profit percentage to finalize the customer price.  
✅ **CAD Image Generation** – Factory managers upload CAD designs, visible to customers.  
✅ **Order Export** –  
   - 📊 **Excel Export**: Store managers can download all orders.  
   - 📄 **PDF Export**: All users can download individual order details.

---

## 👥 User Roles  
1. **Customer** – Requests custom jewelry, views final pricing & CAD images.  
2. **Store Manager** – Manages orders, sets pricing, and exports order data.  
3. **Factory Manager** – Reviews orders, calculates costs, and uploads CAD designs.  

---

## 🛠️ Tech Stack  
- **Backend**: Django (Python)  
- **Database**: MySQL  
- **Frontend**: HTML, CSS, Bootstrap  

---

## 🏗️ Installation & Setup  

### 1. Clone the Repository  
```bash
git clone https://github.com/yourusername/JewelStore-Management.git
cd JewelStore-Management
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure the Database
Create a .env file inside the folder where settings.py is located and add the following database credentials:
```bash
DB_NAME=db_name  
DB_USER=db_user  
DB_PASSWORD=db_password  
DB_HOST=localhost
DB_PORT=3306  
```

### 4. Create a MySQL Database
```bash
CREATE DATABASE db_name;
```

### 5. Run migrations
```bash
python manage.py migrate
python manage.py makemigrations
```

### 6. Import the User groups
```bash
python manage.py loaddata user.json
```

### 7. Create superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to enter a username, email, and password.

### 9. Create static files.
```bash
python manage.py collectstatic
```

### 8. Start the Django Server
```bash
python manage.py runserver
```

### 9. Login to Admin Panel
Go to:
👉 http://127.0.0.1:8000/admin/
Enter the superuser credentials to log in.

---

## 📌 How to Use  

### 🔹 Customer  
1. Visit the store and request a personalized jewelry piece.  
2. Provide a **reference image** and customization details.  
3. Once the order is processed, view:  
   - **Final Price** (after profit margin is added).  
   - **CAD Image** of the custom jewelry.  
4. Download the **PDF invoice** for your order.  

---

### 🔹 Store Manager  
1. **Create a Customer Account**  
   - When a new customer places an order, create a **user account** for them using credentials of your choice.  
2. **Create an Order**  
   - Add customer details, upload reference image, and specify customization options.  
3. **Review Factory Cost**  
   - Once the factory manager calculates the **manufacturing cost**, review the amount.  
4. **Set the Profit Margin**  
   - Apply a percentage (%) profit margin to finalize the **customer price**.  
5. **Export Orders**  
   - Download all orders in **Excel format** for record-keeping.  
6. **Download Order PDF**  
   - Download order details in **PDF format** (for individual orders).  


---

### 🔹 Factory Manager  
1. **Review Orders**  
   - Check new orders and their customization details.  
2. **Calculate Manufacturing Cost**  
   - Determine the total cost to manufacture the jewelry (visible only to factory/store managers).  
3. **Upload CAD Image**  
   - Create and upload a **CAD file** of the jewelry design (visible to customers).  

---

### ⭐ Happy Coding & Enjoy Managing Your Jewel Store!
