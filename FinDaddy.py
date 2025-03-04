import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
from google import genai  # Gemini API

# Initialize Gemini API
API_KEY = "ENTER_YOUR_API_KEY"  # Replace with your actual API key
if API_KEY:
    client = genai.Client(api_key=API_KEY)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css", "/assets/styles.css"], suppress_callback_exceptions=True)
server = app.server  # Required for deployment

# Sample expense categories
categories = ["College", "Loans", "Fun", "Food", "Transportation", "Subscriptions", "Bills", "Shopping", "Miscellaneous"]

# Data storage
df = pd.DataFrame(columns=["Month", "Expense Name", "Category", "Amount"])
income = 0  # Global income variable

# Layout of the app
app.layout = html.Div(className="container", children=[
    html.Div(className="left-panel", children=[
        html.Div(className="input-section", children=[
            html.Button("What's your income?", className="income-btn"),
            dcc.Input(id='income-input', type='number', placeholder='Enter income', className="input-box"),
            html.Button("Set Income", id='set-income-btn', className="set-income-btn", n_clicks=0),
            html.Div(id='income-display', className="income-display"),
            
            html.Button("Monthly Budget", className="budget-btn"),
            dcc.Input(id='budget-input', type='number', placeholder='Enter budget', className="input-box"),
            
            dcc.Input(id='expense-name', type='text', placeholder='Expense Name', className="input-box"),
            dcc.Dropdown(
                id='expense-category', 
                options=[{'label': cat, 'value': cat} for cat in categories],
                placeholder='Select category',
                className="dropdown"
            ),
            dcc.Input(id='expense-amount', type='number', placeholder='Expense Amount', className="input-box"),
            html.Button("Add Expense", id='add-expense-btn', className="expense-btn", n_clicks=0),
        ]),
        html.Div(className="charts", children=[
            html.Div(className="chart-box", id="monthly-spending", children=[
                html.H3("Monthly Spending:"),
                dcc.Graph(id='expense-bar-chart')
            ]),
            html.Div(className="chart-box", id="spending-category", children=[
                html.H3("Spending Category"),
                dcc.Graph(id='expense-pie-chart')
            ])
        ])
    ]),
    html.Div(className="right-panel", children=[
        html.H2("FinDaddy’s here to help!"),
        html.Div(className="advice-box", id="financial-advice"),
        html.Div(className="advice-box", id="gemini-response"),
        dcc.Input(id='user-query', type='text', placeholder='Enter your question?', className="input-box"),
        html.Button("Ask", id='ask-btn', className="ask-btn", n_clicks=0)
    ])
])

# Function to get AI financial advice from Gemini
def get_financial_advice(expense_data, income):
    try:
        prompt = (
            f"User's monthly income: ${income}. Expense breakdown: {expense_data}. Also display the total expenses by the user so far into this month."
            "Act as a parent to the user, and provide structured financial advice in a concise format with bullet points, with a witty, parental undertone. "
            "Limit response to 3 key suggestions, avoiding overly long responses. "
            "Ignore the previous statement if what you are trying to say cannot be simplified into just 3 lines, just try to simplify it."
            "The user is a college student, so keep the advice relevant to that demographic. "
            "Maybe ask the user to treat themselves to something if they stay well within their budget, or to cut back on something if they are overspending."
        )
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        if response and response.text:
            return '\n'.join(response.text.split('\n')[:10]) #Limits output to 10 lines. 
        return "Unable to retrieve advice."
    except Exception as e:
        return f"Error fetching AI advice: {str(e)}"

# Function for chatbot responses
def get_chatbot_response(user_input):
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=user_input)
        if response and response.text:
            return '\n'.join(response.text.split('\n')[:10])  # Limit chatbot response length
        return "I'm not sure how to answer that."
    except Exception as e:
        return f"Error fetching response: {str(e)}"

# Callback to update income
@app.callback(
    Output('income-display', 'children'),
    [Input('set-income-btn', 'n_clicks')],
    [State('income-input', 'value')]
)
def update_income(n_clicks, user_income):
    global income
    if n_clicks > 0 and user_income:
        income = user_income
    return f"Your monthly income is set to: ${income}" if income else "Please enter your income."

# Callback to update expenses & charts
@app.callback(
    [Output('expense-bar-chart', 'figure'), Output('expense-pie-chart', 'figure'), Output('financial-advice', 'children')],
    [Input('add-expense-btn', 'n_clicks')],
    [State('expense-name', 'value'), State('expense-amount', 'value'), State('expense-category', 'value')]
)
def update_dashboard(expense_clicks, expense_name, amount, category):
    global df
    
    if expense_clicks > 0 and amount and category and expense_name:
        df = pd.concat([df, pd.DataFrame([[pd.Timestamp.now().month, expense_name, category, amount]], 
                                          columns=["Month", "Expense Name", "Category", "Amount"])]).reset_index(drop=True)
    
    # Create Bar Chart for Monthly Spending
    bar_fig = px.bar(df, x='Month', y='Amount', color='Category', title='Monthly Spending by Category', barmode='group')
    
    # Create Pie Chart for Spending Breakdown
    pie_fig = px.pie(df, names='Category', values='Amount', title='Spending Breakdown by Category')
    
    # Get AI Financial Advice
    advice = get_financial_advice(df.to_dict(), income) if not df.empty else "Add some expenses to get advice!"
    
    return bar_fig, pie_fig, advice

# Callback for chatbot functionality
@app.callback(
    Output('gemini-response', 'children'),
    [Input('ask-btn', 'n_clicks')],
    [State('user-query', 'value')]
)
def chatbot_response(n_clicks, user_query):
    if n_clicks > 0 and user_query:
        return get_chatbot_response(user_query)
    return ""

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
