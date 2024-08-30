# enhanced_budget_manager_gui_with_advanced_ai.py
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import customtkinter as ctk
from matplotlib.backend_bases import MouseEvent
import pandas as pd
import json
import numpy as np
import ollama  # Assuming ollama is used in AIChat as per main_gui.py

ctk.ThemeManager.load_theme("blue")
ctk.AppearanceModeTracker.set_appearance_mode("Dark")


# AIChat Class for interacting with the AI model
class AIChat:
    def __init__(self, model_name):
        self.model_name = model_name

    def generate_response(self, prompt):
        """Generate a response from the AI model using a prompt."""
        try:
            response = ollama.chat(model=self.model_name, messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"]
        except Exception as e:
            return f"An error occurred while generating the response: {e}"


class BudgetManagerGUI(ctk.CTk):
    def __init__(self, budget_manager):
        super().__init__()
        self.budget_manager = budget_manager
        self.ai_chat = AIChat("llama3.1")  # Instantiate AIChat with the model
        self.title("Enhanced Budget Manager with AI Assistance")
        self.geometry("1200x900")
        self.current_chart = "Pie"  # Track which chart is currently displayed
        self.create_widgets()
       

    def create_widgets(self):
        self.create_income_section()
        self.create_expenses_section()
        self.create_savings_section()
        self.create_chart_section()
        self.create_ai_section()  # Add AI interaction section

    def create_income_section(self):
        # Section for adding income
        self.income_name_entry = ctk.CTkEntry(self, placeholder_text="Income Source Name")
        self.income_name_entry.grid(row=0, column=0, padx=10, pady=10)

        self.income_amount_entry = ctk.CTkEntry(self, placeholder_text="Income Amount")
        self.income_amount_entry.grid(row=0, column=1, padx=10, pady=10)

        self.add_income_button = ctk.CTkButton(self, text="Add Income", command=self.add_income)
        self.add_income_button.grid(row=0, column=2, padx=10, pady=10)

        self.income_list_label = ctk.CTkLabel(self, text="Incomes:")
        self.income_list_label.grid(row=1, column=0, columnspan=3, sticky='w', padx=10)

        self.income_list_box = tk.Listbox(self, height=5)
        self.income_list_box.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky='we')

    def add_income(self):
        """Adds income to the budget manager."""
        name = self.income_name_entry.get()
        try:
            amount = float(self.income_amount_entry.get())
            self.budget_manager.add_income(name, amount)
            self.update_income_list()
            self.income_name_entry.delete(0, tk.END)
            self.income_amount_entry.delete(0, tk.END)
            self.output_label.configure(text=f"Added income: {name} - ${amount:.2f}")
            self.update_graphs()  # Update graphs whenever a new income is added
        except ValueError:
            self.output_label.configure(text="Please enter a valid income amount.")

    def update_income_list(self):
        """Updates the income list display."""
        self.income_list_box.delete(0, tk.END)
        for name, amount in self.budget_manager.incomes.items():
            self.income_list_box.insert(tk.END, f"{name}: ${amount:.2f}")

    def create_expenses_section(self):
        # Section for adding expenses with categories
        self.expense_name_entry = ctk.CTkEntry(self, placeholder_text="Expense Name")
        self.expense_name_entry.grid(row=3, column=0, padx=10, pady=10)

        self.expense_amount_entry = ctk.CTkEntry(self, placeholder_text="Expense Amount")
        self.expense_amount_entry.grid(row=3, column=1, padx=10, pady=10)

        self.expense_category_combobox = ctk.CTkComboBox(
            self, values=["Housing", "Food", "Transportation", "Utilities", "Entertainment", "Healthcare", "Others"]
        )
        self.expense_category_combobox.set("Select Category")
        self.expense_category_combobox.grid(row=3, column=2, padx=10, pady=10)

        self.add_expense_button = ctk.CTkButton(self, text="Add Expense", command=self.add_expense)
        self.add_expense_button.grid(row=3, column=3, padx=10, pady=10)

        self.expense_list_label = ctk.CTkLabel(self, text="Expenses by Category:")
        self.expense_list_label.grid(row=4, column=0, columnspan=4, sticky='w', padx=10)

        self.expense_list_box = tk.Listbox(self, height=10)
        self.expense_list_box.grid(row=5, column=0, columnspan=4, padx=10, pady=10, sticky='we')

    def add_expense(self):
        """Adds an expense to the budget manager with a category."""
        name = self.expense_name_entry.get()
        category = self.expense_category_combobox.get()
        try:
            amount = float(self.expense_amount_entry.get())
            self.budget_manager.add_expense(name, amount, category)
            self.update_expense_list()
            self.expense_name_entry.delete(0, tk.END)
            self.expense_amount_entry.delete(0, tk.END)
            self.expense_category_combobox.set("Select Category")
            self.output_label.configure(text=f"Added expense: {name} - ${amount:.2f} ({category})")
            self.update_graphs()  # Update graphs whenever a new expense is added
        except ValueError:
            self.output_label.configure(text="Please enter a valid expense amount.")

    def update_expense_list(self):
        """Updates the expense list display grouped by category."""
        self.expense_list_box.delete(0, tk.END)
        for category, expenses in self.budget_manager.expenses.items():
            self.expense_list_box.insert(tk.END, f"Category: {category}")
            for name, amount in expenses.items():
                self.expense_list_box.insert(tk.END, f"  {name}: ${amount:.2f}")

    def create_savings_section(self):
        self.output_label = ctk.CTkLabel(self, text="", wraplength=800)
        self.output_label.grid(row=6, column=0, columnspan=4, pady=20)

        # Button to save graph data and images
        self.save_data_button = ctk.CTkButton(self, text="Save Graph Data", command=self.save_graph_data)
        self.save_data_button.grid(row=6, column=3, padx=10, pady=10)

    def create_chart_section(self):
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=7, column=0, columnspan=4, pady=20, sticky="nsew")

        # Chart type buttons
        self.pie_chart_button = ctk.CTkButton(self, text="Pie Chart", command=lambda: self.switch_chart("Pie"))
        self.pie_chart_button.grid(row=8, column=0, padx=5, pady=5)

        self.line_chart_button = ctk.CTkButton(self, text="Line Chart", command=lambda: self.switch_chart("Line"))
        self.line_chart_button.grid(row=8, column=1, padx=5, pady=5)

        self.bar_chart_button = ctk.CTkButton(self, text="Bar Chart", command=lambda: self.switch_chart("Bar"))
        self.bar_chart_button.grid(row=8, column=2, padx=5, pady=5)

        self.scatter_plot_button = ctk.CTkButton(self, text="Scatter Plot", command=lambda: self.switch_chart("Scatter"))
        self.scatter_plot_button.grid(row=8, column=3, padx=5, pady=5)

        # Initial graph placeholders
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.fig.tight_layout(pad=5)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # Initial Graph Drawing
        self.update_graphs()

        # Connect hover event to the tooltip function
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def switch_chart(self, chart_type):
        """Switch between different chart types."""
        self.current_chart = chart_type
        self.update_graphs()

    def update_graphs(self):
        """Update graphs based on the current data and chart type."""
        self.ax.clear()  # Clear existing graphs

        # Gather data
        categories = list(self.budget_manager.expenses.keys())
        values = [sum(self.budget_manager.expenses[cat].values()) for cat in categories]
        total_income = sum(self.budget_manager.incomes.values())

        # Draw the selected chart type
        if self.current_chart == "Pie":
            self.pie_wedges, _, _ = self.ax.pie(values, labels=categories, autopct='%1.1f%%')
            self.ax.set_title('Expense Breakdown by Category')
        elif self.current_chart == "Line":
            months = np.arange(1, 13)
            savings = np.cumsum([self.budget_manager.calculate_monthly_savings() for _ in months])
            self.ax.plot(months, savings, marker='o')
            self.ax.set_title('Savings Over Time')
            self.ax.set_xlabel('Month')
            self.ax.set_ylabel('Savings ($)')
        elif self.current_chart == "Bar":
            self.ax.bar(categories, values, color=['#4CAF50', '#FFC107', '#2196F3', '#FF5722'])
            self.ax.set_title('Expenses by Category')
            self.ax.set_xlabel('Category')
            self.ax.set_ylabel('Amount ($)')
        elif self.current_chart == "Scatter":
            income_values = [total_income] * len(values)
            self.ax.scatter(income_values, values)
            self.ax.set_title('Income vs. Expenses')
            self.ax.set_xlabel('Income ($)')
            self.ax.set_ylabel('Expenses ($)')

        self.canvas.draw()

    def create_ai_section(self):
        """Creates an AI interaction section for asking financial questions."""
        self.ai_input_entry = ctk.CTkEntry(self, placeholder_text="Ask AI for financial advice...")
        self.ai_input_entry.grid(row=1, column=4, columnspan=3, padx=10, pady=10)

        self.ask_ai_button = ctk.CTkButton(self, text="Ask AI", command=self.ask_ai)
        self.ask_ai_button.grid(row=2, column=4, padx=10, pady=10)

        self.ai_response_label = ctk.CTkLabel(self, text="", wraplength=800)
        self.ai_response_label.grid(row=3, column=4, columnspan=4, pady=10)

        # Add buttons for predefined AI tips
        self.budget_tips_button = ctk.CTkButton(self, text="Get Budget Tips", command=self.get_budget_tips)
        self.budget_tips_button.grid(row=4, column=4, padx=5, pady=5)

        self.savings_tips_button = ctk.CTkButton(self, text="Get Savings Tips", command=self.get_savings_tips)
        self.savings_tips_button.grid(row=5, column=4, padx=5, pady=5)

        self.investment_tips_button = ctk.CTkButton(self, text="Get Investment Tips", command=self.get_investment_tips)
        self.investment_tips_button.grid(row=6, column=4, padx=5, pady=5)

    def ask_ai(self):
        """Send the user's question to the AI model and display the response."""
        question = self.ai_input_entry.get()
        response = self.ai_chat.generate_response(question)
        self.ai_response_label.configure(text=response)

    def get_budget_tips(self):
        """Generate AI tips for budgeting based on current financial data."""
        prompt = (
            f"My current monthly income is ${sum(self.budget_manager.incomes.values()):.2f} "
            f"and my total expenses are ${sum(sum(exp.values()) for exp in self.budget_manager.expenses.values()):.2f}. "
            "Can you suggest some tips for better budgeting?"
        )
        response = self.ai_chat.generate_response(prompt)
        self.ai_response_label.configure(text=response)

    def get_savings_tips(self):
        """Generate AI tips for savings based on current financial data."""
        prompt = (
            f"I save approximately ${self.budget_manager.calculate_monthly_savings():.2f} monthly. "
            "Can you suggest ways to increase my savings rate?"
        )
        response = self.ai_chat.generate_response(prompt)
        self.ai_response_label.configure(text=response)

    def get_investment_tips(self):
        """Generate AI tips for investments based on current financial data."""
        prompt = (
            "Based on my current income and expenses, can you suggest some low-risk investment strategies "
            "to grow my savings over time?"
        )
        response = self.ai_chat.generate_response(prompt)
        self.ai_response_label.configure(text=response)

    def on_hover(self, event):
        """Show tooltips when hovering over the chart elements."""
        if self.current_chart == "Pie" and event.inaxes == self.ax:
            for wedge, category, value in zip(self.pie_wedges, categories, values):
                if wedge.contains(event)[0]:
                    self.display_tooltip(event, f"{category}: ${value:.2f}")
                    return
        self.hide_tooltip()

    def display_tooltip(self, event, text):
        """Display tooltip near the cursor."""
        if not hasattr(self, 'tooltip'):
            self.tooltip = self.ax.annotate(
                text, xy=(event.x, event.y), xytext=(10, 10), textcoords='offset points',
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.8),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"),
                fontsize=9
            )
        else:
            self.tooltip.set_text(text)
            self.tooltip.xy = (event.x, event.y)
            self.tooltip.set_visible(True)
        self.fig.canvas.draw_idle()

    def hide_tooltip(self):
        """Hide the tooltip."""
        if hasattr(self, 'tooltip'):
            self.tooltip.set_visible(False)
            self.fig.canvas.draw_idle()

    def save_graph_data(self):
        """Save graph data and images to the local filesystem."""
        data = {
            "incomes": self.budget_manager.incomes,
            "expenses": self.budget_manager.expenses
        }
        with open("graph_data.json", "w") as file:
            json.dump(data, file, indent=4)
        self.output_label.configure(text="Graph data saved as 'graph_data.json'.")
        self.fig.savefig("graphs.png")
        self.output_label.configure(text="Graphs saved as 'graphs.png'.")
        print("Graph data and images saved successfully.")

    def on_click(self, event: MouseEvent):
        if event.inaxes in [self.ax]:
            print(f"Clicked on {event.xdata}, {event.ydata}")

    def show_details(self, x, y):
        if x < self.budget_manager.annual_income:
            print("Clicked on Expenses section.")
        else:
            print("Clicked on Income section.")


class BudgetManager:
    def __init__(self, age=0, annual_income=0):
        self.age = age
        self.annual_income = annual_income
        self.monthly_income = annual_income / 12
        self.expenses = {}  # Now stores expenses grouped by category
        self.bills = {}
        self.investments = {}
        self.debts = {}
        self.financial_goals = {}
        self.savings = 0
        self.incomes = {}  # Dictionary to hold income sources

    def add_income(self, name, amount):
        """Add an income source to the budget."""
        self.incomes[name] = amount

    def add_expense(self, name, amount, category):
        """Add an expense to the budget under a specific category."""
        if category not in self.expenses:
            self.expenses[category] = {}
        self.expenses[category][name] = amount

    def add_bill(self, name, amount):
        self.bills[name] = amount

    def add_investment(self, name, amount, annual_return_rate):
        self.investments[name] = {"amount": amount, "rate": annual_return_rate}

    def add_debt(self, name, amount, interest_rate, monthly_payment):
        self.debts[name] = {
            "amount": amount,
            "interest_rate": interest_rate,
            "monthly_payment": monthly_payment,
        }

    def add_goal(self, name, target_amount):
        self.financial_goals[name] = {"target_amount": target_amount, "current_amount": 0}

    def contribute_to_goal(self, name, amount):
        if name in self.financial_goals:
            self.financial_goals[name]["current_amount"] += amount
        else:
            print(f"Goal '{name}' not found.")

    def calculate_monthly_savings(self):
        total_expenses = sum(sum(exp.values()) for exp in self.expenses.values())
        total_bills = sum(self.bills.values())
        total_debt_payments = sum(debt["monthly_payment"] for debt in self.debts.values())
        self.savings = self.monthly_income - (total_expenses + total_bills + total_debt_payments)
        return self.savings

    def estimate_retirement_amount(self, desired_retirement_age):
        years_until_retirement = desired_retirement_age - self.age
        if years_until_retirement <= 0:
            return "You are already at or past your desired retirement age."

        current_savings = sum(inv["amount"] for inv in self.investments.values())
        estimated_growth = current_savings

        for _ in range(years_until_retirement):
            estimated_growth += estimated_growth * 0.05  # Assuming 5% annual growth

        return estimated_growth

    def save_data(self, filename="budget_data.json"):
        data = {
            "age": self.age,
            "annual_income": self.annual_income,
            "expenses": self.expenses,
            "bills": self.bills,
            "investments": self.investments,
            "debits": self.debts,
            "financial_goals": self.financial_goals,
            "incomes": self.incomes,
        }
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data saved to {filename}")

    def load_data(self, filename="budget_data.json"):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                self.age = data["age"]
                self.annual_income = data["annual_income"]
                self.expenses = data["expenses"]
                self.bills = data["bills"]
                self.investments = data["investments"]
                self.debts = data["debits"]
                self.financial_goals = data["financial_goals"]
                self.incomes = data["incomes"]
            print(f"Data loaded from {filename}")
        except FileNotFoundError:
            print(f"No data file found with the name {filename}")


if __name__ == "__main__":
    # Create BudgetManager instance with default parameters
    budget_manager = BudgetManager(age=30, annual_income=50000)  
    # Launch the GUI with the budget manager instance
    app = BudgetManagerGUI(budget_manager)
    app.mainloop()
