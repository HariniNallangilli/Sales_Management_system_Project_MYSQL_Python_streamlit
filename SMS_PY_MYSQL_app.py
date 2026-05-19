import streamlit as st
import pandas as pd
#import pyodbc
import mysql.connector

conn = mysql.connector.connect(
 host="localhost",
 user="root",
 password="test123",
 database="Sales_Management_System"
 )

cursor = conn.cursor()
#print("Connected Successfully")
# KeyError:# 'st.session_state has no key "role". Did you forget to initialize it?'
# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'role' not in st.session_state:
    st.session_state['role'] = None

if 'branch_id' not in st.session_state:
    st.session_state['branch_id'] = None

if 'username' not in st.session_state:
    st.session_state['username'] = None


#LOGIN PAGE
if not st.session_state['logged_in']:

    st.title("Sales Management Application Login")

    username = st.text_input("User name:")
    password = st.text_input("Password:", type="password")

    if st.button("Login"):

        users_query = f"""
        SELECT * FROM users
        WHERE username='{username}'
        AND password_hash='{password}'
        """

        df_users = pd.read_sql(users_query, conn)

        if len(df_users) > 0:

            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.session_state['role'] = df_users.loc[0, 'role'] # [0,col] value ofrom 0th index 
            st.session_state['branch_id'] = df_users.loc[0, 'branch_id']

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Credentials")


# AFTER LOGIN 
else:
    #assigning role from session to a variable"role",branch_id to use in else block
    role = st.session_state['role']
    branch_id = st.session_state['branch_id']

    # Sidebar
    st.sidebar.title("Sales Management")
    st.sidebar.write(f"Logged in as: **{st.session_state['username']}**")
    st.sidebar.write(f"Role: **{role}**")

    page = st.sidebar.radio("Navigate",
        ["Add Sales", "Add Payment", "View Sales","Insights & Reporting"])

    # Logout
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    # Add Sales 
    if page == "Add Sales":

        st.header("Add Sales") 
        
        if role == 'Super Admin': #filter branch from super user while adding sales
            df_branches = pd.read_sql("SELECT branch_id, branch_name FROM branches", conn)
            branch_options = {f"{row['branch_name ']} (ID: {row['branch_id']})": row['branch_id'] for _, row in df_branches.iterrows()}
            
            selected_branch = st.selectbox("Select Branch", list(branch_options.keys()))
            target_branch_id = int(branch_options[selected_branch])
            customer_name = st.text_input("Customer Name")
            mobile = st.text_input("Mobile Number")
            product = st.selectbox("Product",['DS', 'DA', 'BA', 'FSD'])
            amount = st.number_input("Gross Sales")
        else:
             # Regular Admin-
             target_branch_id = int(branch_id)
             st.info(f" Your Branch ID: {target_branch_id}")
         
             customer_name = st.text_input("Customer Name")
             mobile = st.text_input("Mobile Number")
             product = st.selectbox("Product",['DS', 'DA', 'BA', 'FSD'])
             amount = st.number_input("Gross Sales")

        if st.button("Save Sale"):

            cursor = conn.cursor() #cursor connected to SQL

            csi_query = """
            INSERT INTO customer_sales
            (
                branch_id,
                sale_date,
                customer_name,
                mobile_number,
                product_name,
                gross_sales
            )
            VALUES (%s, NOW(), %s, %s, %s, %s)
            """
             #execute - inserts values into cus_sales table
            cursor.execute(
                csi_query, ( int(target_branch_id),str(customer_name)
                            ,str(mobile),str(product),float(amount))
                           )
            conn.commit()
            st.success("Sales Added Successfully")
            cursor.close()# Free up database memory
 
     # Add Payment Page
    elif page == "Add Payment":

        st.header("Add Payment Split")
        sale_id = st.number_input("Sale ID", step=1)
        amount_paid = st.number_input("Amount Paid")

        payment_method = st.selectbox("Payment Method",['Cash', 'UPI', 'Card'])

        if st.button("Add Payment"):

            cursor = conn.cursor()
            ps_query = """
            INSERT INTO payment_splits
            (
                sale_id,payment_date,amount_paid,payment_method
            )
            VALUES (%s, NOW(), %s, %s)
            """

            cursor.execute(
                ps_query,(int(sale_id), 
                    float(amount_paid), 
                    str(payment_method))
            )
            conn.commit()
            st.success("Payment Added Successfully")

    # View Sales Page
    elif page == "View Sales":
        st.header("Sales Records & KPI Dashboard")
        if role == 'Super Admin':
             df_branches = pd.read_sql("SELECT branch_id, branch_name FROM branches", conn)
             branch_options = {f"{row['branch_name']} (ID: {row['branch_id']})": row['branch_id'] for _, row in df_branches.iterrows()}
            
             # Adding 'All Branches' option for super user
             options_list = ["All Branches"] + list(branch_options.keys())
             selected_filter = st.selectbox("Choose Branch", options_list)
             
             #Pull summed values based on the branch selection
             if selected_filter == "All Branches":
                sales_query = "SELECT SUM(gross_sales) as total_sales FROM customer_sales"
                payments_query = "SELECT SUM(amount_paid) as total_received FROM payment_splits"
                branch_query = "SELECT * FROM customer_sales"
             else:
                selected_branch_id = int(branch_options[selected_filter])
                sales_query = f"SELECT SUM(gross_sales) as total_sales FROM customer_sales WHERE branch_id = {selected_branch_id}"
                payments_query = f"""
                    SELECT SUM(p.amount_paid) as total_received 
                    FROM payment_splits p
                    JOIN customer_sales c ON p.sale_id = c.sale_id
                    WHERE c.branch_id = {selected_branch_id}
                """
                branch_query = f"SELECT * FROM customer_sales WHERE branch_id = {selected_branch_id}"
              
                     
             df_sales_sum = pd.read_sql(sales_query, conn)
             df_payments_sum = pd.read_sql(payments_query, conn)
             df_branch = pd.read_sql(branch_query, conn)
            
        else:
            #Showing total sales & recvd/pending payments from particular branch
                
            sales_query = f"SELECT SUM(gross_sales) as total_sales FROM customer_sales WHERE branch_id = {int(branch_id)}"
            payments_query = f"""
                SELECT SUM(p.amount_paid) as total_received 
                FROM payment_splits p
                JOIN customer_sales c ON p.sale_id = c.sale_id
                WHERE c.branch_id = {int(branch_id)}
            """
            branch_query = f"SELECT * FROM customer_sales WHERE branch_id = {int(branch_id)}"
            
            df_sales_sum = pd.read_sql(sales_query, conn)
            df_payments_sum = pd.read_sql(payments_query, conn)
            df_branch = pd.read_sql(branch_query, conn)
         #KPI calcs for both superadmin and regular admin               
        total_sales = float(df_sales_sum['total_sales'].fillna(0).iloc[0])
        total_received = float(df_payments_sum['total_received'].fillna(0).iloc[0])
        pending_amount = total_sales - total_received
            
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Sales", value=f"₹{total_sales:,.2f}")
        with col2:
            st.metric(label="Received Amount", value=f"₹{total_received:,.2f}", delta_color="normal")
        with col3:
            st.metric(label="Pending Amount", value=f"₹{pending_amount:,.2f}", delta=f"-₹{pending_amount:,.2f}" if pending_amount > 0 else "0.00")
            
        st.markdown("---")
        st.subheader("Branch Performance Summary Dashboard")
        st.dataframe(df_branch, use_container_width=True)
        
     #Insights & Reporting Page
    elif page == "Insights & Reporting":
        st.header("Sale Insights & Reports")
        # Query for selecting role/branch based sales and payments for overall business revenue
        
        if role == 'Super Admin':
            df_sales_all = pd.read_sql("""SELECT s.*, b.branch_name FROM customer_sales s 
                                       JOIN branches b ON s.branch_id = b.branch_id""", conn)
            df_payments_all = pd.read_sql("""SELECT p.*, s.branch_id FROM payment_splits p 
                                          JOIN customer_sales s ON p.sale_id = s.sale_id""", conn)
        else:
            df_sales_all = pd.read_sql(f"""SELECT s.*, b.branch_name FROM customer_sales s
                                       JOIN branches b ON s.branch_id = b.branch_id WHERE s.branch_id = {int(branch_id)}""", conn)
            df_payments_all = pd.read_sql(f"""SELECT p.*, s.branch_id FROM payment_splits p 
                                          JOIN customer_sales s ON p.sale_id = s.sale_id WHERE s.branch_id = {int(branch_id)}""", conn)
        
      #Total received amount , total pending amount,Pending collection percentage.
        total_sale_amount = float(df_sales_all['gross_sales'].sum())
        total_recd = float(df_payments_all['amount_paid'].sum())
        total_pend = total_sale_amount - total_recd
        pending_pct = (total_pend / total_sale_amount * 100) 
            
      #KPI 
        st.subheader("KPI Summary")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Overall Business Revenue", f"₹{total_recd:,.2f}")
        kpi2.metric("Total Received Amount", f"₹{total_recd:,.2f}")
        kpi3.metric("Total Pending Amount", f"₹{total_pend:,.2f}")
        #kpi4.metric("Pending Collection %", f"{pending_pct:.1f}%", 
        # delta=f"{pending_pct:.1f}% Risk", delta_color="inverse" if pending_pct > 0 else "normal")
            
        st.markdown("---")
    
       # 4. Branch Comparisons & Payments Chart
        col_br1, col_br2 = st.columns(2)
            
        with col_br1:
                st.subheader("Branch-wise sales comparison report")
                # Group data dynamically by location fields
                branch_chart_data = df_sales_all.groupby('branch_name')['gross_sales'].sum().reset_index()
                branch_chart_data = branch_chart_data.set_index('branch_name')
                st.bar_chart(branch_chart_data)
                
        with col_br2:
                st.subheader("Payment Method Analysis")
                #if not df_payments_all.empty:
                pay_chart_data = df_payments_all.groupby('payment_method')['amount_paid'].sum().reset_index()
                pay_chart_data = pay_chart_data.set_index('payment_method')
                st.bar_chart(pay_chart_data)
                #else:
                #   st.info("No collections logs discovered to map distribution methods.")

        st.markdown("---")




        