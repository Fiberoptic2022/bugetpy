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

    def reset_conversation(self):
        """Reset the conversation with the AI model."""
        # Add reset logic if applicable, otherwise a simple placeholder:
        print("Conversation reset.")


class BudgetManagerGUI(ctk.CTk):
    def __init__(self, budget_manager):
        super().__init__()
        self.budget_manager = budget_manager
        self.ai_chat = AIChat("llama3.1")
        ctk.set_appearance_mode("dark")  # Set appearance to dark mode
        self.title("Enhanced Budget Manager with AI Assistance")
        self.geometry("1400x1050")
        self.current_chart = "Pie"  # Default chart type
        self.create_widgets()

    def create_widgets(self):
        """Set up the main UI layout and all sections."""
        self.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.create_income_section()
        self.create_expenses_section()
        self.create_savings_section()
        self.create_chart_section()
        self.create_ai_section()
        self.create_export_section()
        self.create_budget_summary_section()  # New Summary Section
        self.create_goal_tracking_section()   # New Goal Tracking Section

    # 1. Monthly Budget Summary Section
    def create_budget_summary_section(self):
        """Creates a summary of the user's monthly budget, including total income, expenses, and savings."""
        summary_frame = ctk.CTkFrame(self)
        summary_frame.grid(row=8, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
        
        self.income_summary_label = ctk.CTkLabel(summary_frame, text="Total Monthly Income: $0.00", font=("Arial", 14))
        self.income_summary_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.expense_summary_label = ctk.CTkLabel(summary_frame, text="Total Monthly Expenses: $0.00", font=("Arial", 14))
        self.expense_summary_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        self.savings_summary_label = ctk.CTkLabel(summary_frame, text="Total Monthly Savings: $0.00", font=("Arial", 14))
        self.savings_summary_label.grid(row=0, column=2, padx=10, pady=10, sticky="w")

        # Call update to display initial values
        self.update_budget_summary()

    def update_budget_summary(self):
        """Update the budget summary section with the latest income, expenses, and savings."""
        total_income = sum(self.budget_manager.incomes.values())
        total_expenses = sum(sum(exp.values()) for exp in self.budget_manager.expenses.values())
        total_savings = self.budget_manager.calculate_monthly_savings()

        self.income_summary_label.configure(text=f"Total Monthly Income: ${total_income:.2f}")
        self.expense_summary_label.configure(text=f"Total Monthly Expenses: ${total_expenses:.2f}")
        self.savings_summary_label.configure(text=f"Total Monthly Savings: ${total_savings:.2f}")

    # 2. Goal Tracking Section
    def create_goal_tracking_section(self):
        """Create a section to add and track financial goals."""
        goal_frame = ctk.CTkFrame(self)
        goal_frame.grid(row=9, column=0, columnspan=5, padx=10, pady=10, sticky="nsew")
        
        self.goal_name_entry = ctk.CTkEntry(goal_frame, placeholder_text="Goal Name", width=200)
        self.goal_name_entry.grid(row=0, column=0, padx=5, pady=5)

        self.goal_amount_entry = ctk.CTkEntry(goal_frame, placeholder_text="Target Amount", width=150)
        self.goal_amount_entry.grid(row=0, column=1, padx=5, pady=5)

        self.add_goal_button = ctk.CTkButton(goal_frame, text="Add Goal", command=self.add_goal)
        self.add_goal_button.grid(row=0, column=2, padx=5, pady=5)

        self.contribute_amount_entry = ctk.CTkEntry(goal_frame, placeholder_text="Contribution Amount", width=150)
        self.contribute_amount_entry.grid(row=1, column=0, padx=5, pady=5)

        self.goal_listbox = tk.Listbox(goal_frame, height=5, bg='#2b2b2b', fg='white')
        self.goal_listbox.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="we")

        self.contribute_button = ctk.CTkButton(goal_frame, text="Contribute to Goal", command=self.contribute_to_goal)
        self.contribute_button.grid(row=1, column=3, padx=5, pady=5)

        self.update_goal_list()

    def add_goal(self):
        """Adds a new financial goal."""
        name = self.goal_name_entry.get()
        try:
            amount = float(self.goal_amount_entry.get())
            self.budget_manager.add_goal(name, amount)
            self.goal_name_entry.delete(0, tk.END)
            self.goal_amount_entry.delete(0, tk.END)
            self.update_goal_list()
        except ValueError:
            self.output_label.configure(text="Please enter a valid target amount.")

    def contribute_to_goal(self):
        """Contributes a specified amount to the selected goal."""
        selected = self.goal_listbox.curselection()
        if selected:
            goal_name = self.goal_listbox.get(selected).split(":")[0]
            try:
                amount = float(self.contribute_amount_entry.get())
                self.budget_manager.contribute_to_goal(goal_name, amount)
                self.update_goal_list()
                self.contribute_amount_entry.delete(0, tk.END)
            except ValueError:
                self.output_label.configure(text="Please enter a valid contribution amount.")

    def update_goal_list(self):
        """Updates the goal list with current goals and their progress."""
        self.goal_listbox.delete(0, tk.END)
        for goal_name, goal_info in self.budget_manager.financial_goals.items():
            target = goal_info["target_amount"]
            current = goal_info["current_amount"]
            progress = (current / target) * 100
            self.goal_listbox.insert(tk.END, f"{goal_name}: ${current:.2f} / ${target:.2f} ({progress:.1f}%)")


    def create_ai_section(self):
        """Create an AI interaction section for asking financial questions."""
        ai_frame = ctk.CTkFrame(self)
        ai_frame.grid(row=3, column=4, columnspan=3, rowspan=6, padx=20, pady=10, sticky="nsew")
        
        # Set grid configuration for the AI frame
        ai_frame.grid_columnconfigure((0, 1, 2), weight=1)
        ai_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # AI input field
        self.ai_input_entry = ctk.CTkEntry(ai_frame, placeholder_text="Ask AI for financial advice...", width=400)
        self.ai_input_entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Ask AI button
        self.ask_ai_button = ctk.CTkButton(ai_frame, text="Ask AI", command=self.ask_ai)
        self.ask_ai_button.grid(row=0, column=3, padx=10, pady=10)

        # AI response text box
        self.ai_text_box = ctk.CTkTextbox(ai_frame, height=150, width=400, wrap='word')
        self.ai_text_box.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.ai_text_box.insert("0.0", "Welcome to the AI Financial Advisor!\nAsk me any questions about budgeting, savings, investments, or retirement.")

        # Button section
        button_frame = ctk.CTkFrame(ai_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Set grid configuration for the button frame
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Add AI feature buttons with consistent size and spacing
        self.budget_tips_button = ctk.CTkButton(button_frame, text="Get Budget Tips", command=self.get_budget_tips, width=150)
        self.budget_tips_button.grid(row=0, column=0, padx=5, pady=5)

        self.savings_tips_button = ctk.CTkButton(button_frame, text="Get Savings Tips", command=self.get_savings_tips, width=150)
        self.savings_tips_button.grid(row=0, column=1, padx=5, pady=5)

        self.investment_tips_button = ctk.CTkButton(button_frame, text="Get Investment Tips", command=self.get_investment_tips, width=150)
        self.investment_tips_button.grid(row=0, column=2, padx=5, pady=5)

        self.retirement_tips_button = ctk.CTkButton(button_frame, text="Get Retirement Tips", command=self.get_retirement_tips, width=150)
        self.retirement_tips_button.grid(row=0, column=3, padx=5, pady=5)

        self.reset_conversation_button = ctk.CTkButton(button_frame, text="Reset Conversation", command=self.reset_conversation, width=150)
        self.reset_conversation_button.grid(row=0, column=4, padx=5, pady=5)

    def ask_ai(self):
        """Send a question to the AI and display the response."""
        question = self.ai_input_entry.get()
        if question:
            response = self.ai_chat.generate_response(question)
            self.ai_text_box.delete(1.0, tk.END)  # Clear previous responses
            self.ai_text_box.insert(tk.END, response)

    # Define the other required methods such as get_budget_tips, get_savings_tips, etc.
    # Example:
    def get_budget_tips(self):
        prompt = "Provide tips for managing a budget effectively."
        response = self.ai_chat.generate_response(prompt)
        self.display_ai_response(response)

    def display_ai_response(self, response):
        """Helper function to display the AI response in the text box."""
        self.ai_text_box.delete(1.0, tk.END)  # Clear previous response
        if response:
            self.ai_text_box.insert(tk.END, response)
        else:
            self.ai_text_box.insert(tk.END, "Unable to fetch a response. Please try again.")


    def create_income_section(self):
        """Creates the income input and list section."""
        self.income_name_entry = ctk.CTkEntry(self, placeholder_text="Income Source Name", width=200)
        self.income_name_entry.grid(row=0, column=0, padx=10, pady=10)

        self.income_amount_entry = ctk.CTkEntry(self, placeholder_text="Income Amount", width=100)
        self.income_amount_entry.grid(row=0, column=1, padx=10, pady=10)

        self.add_income_button = ctk.CTkButton(self, text="Add Income", command=self.add_income)
        self.add_income_button.grid(row=0, column=2, padx=10, pady=10)

        self.remove_income_button = ctk.CTkButton(self, text="Remove Income", command=self.remove_income)
        self.remove_income_button.grid(row=0, column=3, padx=10, pady=10)

        self.income_list_label = ctk.CTkLabel(self, text="Incomes:")
        self.income_list_label.grid(row=1, column=0, columnspan=4, sticky='w', padx=10)

        self.income_list_box = tk.Listbox(self, height=5, bg='#2b2b2b', fg='white')
        self.income_list_box.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky='we')
        self.update_income_list_box()

    def create_expenses_section(self):
        """Creates the expense input and list section with categories."""
        self.expense_name_entry = ctk.CTkEntry(self, placeholder_text="Expense Name", width=200)
        self.expense_name_entry.grid(row=3, column=0, padx=10, pady=10)

        self.expense_amount_entry = ctk.CTkEntry(self, placeholder_text="Expense Amount", width=100)
        self.expense_amount_entry.grid(row=3, column=1, padx=10, pady=10)

        self.expense_category_combobox = ctk.CTkComboBox(
        self, values=["Housing", "Food", "Transportation", "Utilities", "Entertainment", "Healthcare", "Others"], width=150)
        self.expense_category_combobox.set("Select Category")
        self.expense_category_combobox.grid(row=3, column=2, padx=10, pady=10)

        self.add_expense_button = ctk.CTkButton(self, text="Add Expense", command=self.add_expense)
        self.add_expense_button.grid(row=3, column=3, padx=10, pady=10)

        self.remove_expense_button = ctk.CTkButton(self, text="Remove Expense", command=self.remove_expense)
        self.remove_expense_button.grid(row=4, column=3, padx=10, pady=10)

        self.expense_list_label = ctk.CTkLabel(self, text="Expenses by Category:")
        self.expense_list_label.grid(row=5, column=0, columnspan=5, sticky='w', padx=10)

        self.expense_list_box = tk.Listbox(self, height=10, bg='#2b2b2b', fg='white')
        self.expense_list_box.grid(row=6, column=0, columnspan=5, padx=10, pady=10, sticky='we')
        self.update_expense_list_box()

    def update_income_list_box(self):
        """Updates the income list box with current data."""
        self.income_list_box.delete(0, tk.END)
        for name, amount in self.budget_manager.incomes.items():
            self.income_list_box.insert(tk.END, f"{name}: ${amount:.2f}")

    def update_expense_list_box(self):
        """Updates the expense list box with current data."""
        self.expense_list_box.delete(0, tk.END)
        for category, expenses in self.budget_manager.expenses.items():
            self.expense_list_box.insert(tk.END, f"Category: {category}")
            for name, amount in expenses.items():
                self.expense_list_box.insert(tk.END, f"  {name}: ${amount:.2f}")

    def add_income(self):
        """Adds income to the budget manager."""
        name = self.income_name_entry.get()
        try:
            amount = float(self.income_amount_entry.get())
            self.budget_manager.add_income(name, amount)
            self.update_income_list_box()
            self.income_name_entry.delete(0, tk.END)
            self.income_amount_entry.delete(0, tk.END)
            self.output_label.configure(text=f"Added income: {name} - ${amount:.2f}")
            self.update_graphs()
        except ValueError:
            self.output_label.configure(text="Please enter a valid income amount.")

    def remove_income(self):
        """Removes selected income from the budget manager."""
        selected = self.income_list_box.curselection()
        if selected:
            name = self.income_list_box.get(selected).split(":")[0]
            del self.budget_manager.incomes[name]
            self.update_income_list_box()
            self.output_label.configure(text=f"Removed income: {name}")

    def add_expense(self):
        """Adds an expense to the budget manager with a category."""
        name = self.expense_name_entry.get()
        category = self.expense_category_combobox.get()
        try:
            amount = float(self.expense_amount_entry.get())
            self.budget_manager.add_expense(name, amount, category)
            self.update_expense_list_box()
            self.expense_name_entry.delete(0, tk.END)
            self.expense_amount_entry.delete(0, tk.END)
            self.expense_category_combobox.set("Select Category")
            self.output_label.configure(text=f"Added expense: {name} - ${amount:.2f} ({category})")
            self.update_graphs()
        except ValueError:
            self.output_label.configure(text="Please enter a valid expense amount.")

    def remove_expense(self):
        """Removes selected expense from the budget manager."""
        selected = self.expense_list_box.curselection()
        if selected:
            # Extract the category and name from the selected item in the list box
            selected_item = self.expense_list_box.get(selected[0])
            if "Category:" in selected_item:
                # Avoid selecting category labels
                self.output_label.configure(text="Please select an expense to remove, not a category.")
                return

            # Extract category and name from the selected line
            category_name = self.expense_list_box.get(selected[0] - 1).split(": ")[1]
            expense_name = selected_item.strip().split(": ")[0].strip()

            # Remove expense from the budget manager
            if category_name in self.budget_manager.expenses and expense_name in self.budget_manager.expenses[category_name]:
                del self.budget_manager.expenses[category_name][expense_name]
                # Remove category if no expenses left
                if not self.budget_manager.expenses[category_name]:
                    del self.budget_manager.expenses[category_name]

                # Update the expense list display
                self.update_expense_list_box()
                self.output_label.configure(text=f"Removed expense: {expense_name} from {category_name}")
            else:
                self.output_label.configure(text="Expense not found.")


    def create_savings_section(self):
        """Create savings section to display output messages."""
        self.output_label = ctk.CTkLabel(self, text="", wraplength=800)
        self.output_label.grid(row=6, column=0, columnspan=5, pady=20)

        # Button to save graph data and images
        self.save_data_button = ctk.CTkButton(self, text="Save Graph Data", command=self.save_graph_data)
        self.save_data_button.grid(row=6, column=4, padx=10, pady=10)

    def create_chart_section(self):
        """Create a refined chart section with various chart options and responsive layout."""
        # Create a frame dedicated to chart display and configuration
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.grid(row=7, column=0, columnspan=4, pady=20, sticky="nsew")
        self.chart_frame.grid_rowconfigure(1, weight=1)  # Ensure chart expands vertically
        self.chart_frame.grid_columnconfigure(0, weight=1)  # Ensure chart expands horizontally

        # Sub-frame for chart type buttons to keep them separated from the chart itself
        button_frame = ctk.CTkFrame(self.chart_frame)
        button_frame.grid(row=0, column=0, padx=10, pady=(0, 10), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.bar_charts_button = ctk.CTkButton(button_frame, text="Bar Charts", command=lambda: self.switch_chart("Bar"))
        self.bar_charts_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.pie_charts_button = ctk.CTkButton(button_frame, text="Pie Charts", command=lambda: self.switch_chart("Pie"))
        self.pie_charts_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.line_charts_button = ctk.CTkButton(button_frame, text="Line Charts", command=lambda: self.switch_chart("Line"))
        self.line_charts_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.scatter_plots_button = ctk.CTkButton(button_frame, text="Scatter Plots", command=lambda: self.switch_chart("Scatter"))
        self.scatter_plots_button.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        self.fig = Figure(figsize=(10, 6), dpi=100)  
        self.ax = self.fig.add_subplot(111)  

        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()


        # Create chart type buttons with improved alignment and spacing
        chart_buttons = [
            ("Pie Chart", "Pie"),
            ("Line Chart", "Line"),
            ("Bar Chart", "Bar"),
            ("Scatter Plot", "Scatter"),
        ]
        for i, (text, chart_type) in enumerate(chart_buttons):
            ctk.CTkButton(
                button_frame,
                text=text,
                command=lambda ct=chart_type: self.switch_chart(ct),
                width=100
            ).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        # Create and configure the figure and axes for displaying charts
        self.fig, self.ax = plt.subplots(figsize=(10, 6))  # Adjust size as needed
        self.fig.tight_layout(pad=3)  # Adjust padding to avoid overlap

        # Embed the figure into a canvas within the chart frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew")  # Use grid for better resizing control

        # Bind events to the canvas for interaction, such as tooltips
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)

        # Initial drawing of the graph based on the current data and selected chart type
        self.update_graphs()

    def switch_chart(self, chart_type):
        """Switch between different chart types."""
        self.current_chart = chart_type
        self.update_graphs()

    def update_graphs(self):
        """Update graphs based on the current data and chart type."""
        self.ax.clear()  # Clear existing graphs

        # Gather data
        self.categories = list(self.budget_manager.expenses.keys())
        self.values = [sum(self.budget_manager.expenses[cat].values()) for cat in self.categories]
        total_income = sum(self.budget_manager.incomes.values())

        # Draw the selected chart type
        if self.current_chart == "Pie":
            self.pie_wedges, _, _ = self.ax.pie(self.values, labels=self.categories, autopct='%1.1f%%')
            self.ax.set_title('Expense Breakdown by Category')
        elif self.current_chart == "Line":
            months = np.arange(1, 13)
            savings = np.cumsum([self.budget_manager.calculate_monthly_savings() for _ in months])
            self.ax.plot(months, savings, marker='o')
            self.ax.set_title('Savings Over Time')
            self.ax.set_xlabel('Month')
            self.ax.set_ylabel('Savings ($)')
        elif self.current_chart == "Bar":
            # Check if categories and values are present
            if not self.categories or not self.values:
                self.ax.text(0.5, 0.5, "No data available to display.", ha='center', va='center', fontsize=12)
            else:
                # Dynamically adjust based on the number of categories
                max_categories = 10
                rotation_angle = 45 if len(self.categories) > max_categories else 0
                bar_width = max(0.8 - (len(self.categories) * 0.05), 0.2)  # Adjust width dynamically
                font_size = max(12 - len(self.categories), 8)  # Font size reduces slightly with more categories

                # Plot bar chart with dynamic adjustments
                bars = self.ax.bar(self.categories, self.values, color=['#4CAF50', '#FFC107', '#2196F3', '#FF5722'], width=bar_width)

                # Enhance readability
                self.ax.set_title('Expenses by Category', fontsize=14)
                self.ax.set_xlabel('Category', fontsize=12)
                self.ax.set_ylabel('Amount ($)', fontsize=12)

                # Adjust x-ticks to avoid overlapping labels
                self.ax.set_xticks(range(len(self.categories)))
                self.ax.set_xticklabels(self.categories, rotation=rotation_angle, ha='right', fontsize=font_size, wrap=True)

                # Add gridlines for easier comparison
                self.ax.grid(axis='y', linestyle='--', alpha=0.6)

                # Annotate bars with values for better insight
                for bar in bars:
                    yval = bar.get_height()
                    self.ax.text(
                        bar.get_x() + bar.get_width() / 2, yval,
                        f'${yval:.2f}',
                        ha='center', va='bottom', fontsize=font_size, color='black'
                    )

                # Prevent labels from being clipped
                self.fig.tight_layout(pad=3)
                self.ax.margins(0.1)  # Add some margin to the plot to avoid clipping bars

        elif self.current_chart == "Scatter":
            income_values = [total_income] * len(self.values)
            self.ax.scatter(income_values, self.values)
            self.ax.set_title('Income vs. Expenses')
            self.ax.set_xlabel('Income ($)')
            self.ax.set_ylabel('Expenses ($)')

        # Redraw the canvas to update the graph
        self.canvas.draw()




    def on_hover(self, event):
        """Show tooltips when hovering over the chart elements."""
        if self.current_chart == "Pie" and event.inaxes == self.ax:
            for wedge, category, value in zip(self.pie_wedges, self.categories, self.values):
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

    def create_ai_section(self):
        """Create an AI interaction section for asking financial questions."""
        ai_frame = ctk.CTkFrame(self)
        ai_frame.grid(row=3, column=4, columnspan=3, rowspan=6, padx=20, pady=10, sticky="nsew")
        
        # Set grid configuration for the AI frame
        ai_frame.grid_columnconfigure((0, 1, 2), weight=1)
        ai_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        # AI input field
        self.ai_input_entry = ctk.CTkEntry(ai_frame, placeholder_text="Ask AI for financial advice...", width=400)
        self.ai_input_entry.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Ask AI button
        self.ask_ai_button = ctk.CTkButton(ai_frame, text="Ask AI", command=self.ask_ai)
        self.ask_ai_button.grid(row=0, column=3, padx=10, pady=10)

        # AI response text box
        self.ai_text_box = ctk.CTkTextbox(ai_frame, height=150, width=400, wrap='word')
        self.ai_text_box.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.ai_text_box.insert("0.0", "Welcome to the AI Financial Advisor!\nAsk me any questions about budgeting, savings, investments, or retirement.")

        # Button section
        button_frame = ctk.CTkFrame(ai_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10, sticky="nsew")
        
        # Set grid configuration for the button frame
        button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Add AI feature buttons with consistent size and spacing
        self.budget_tips_button = ctk.CTkButton(button_frame, text="Get Budget Tips", command=self.get_budget_tips, width=150)
        self.budget_tips_button.grid(row=0, column=0, padx=5, pady=5)

        self.savings_tips_button = ctk.CTkButton(button_frame, text="Get Savings Tips", command=self.get_savings_tips, width=150)
        self.savings_tips_button.grid(row=0, column=1, padx=5, pady=5)

        self.investment_tips_button = ctk.CTkButton(button_frame, text="Get Investment Tips", command=self.get_investment_tips, width=150)
        self.investment_tips_button.grid(row=0, column=2, padx=5, pady=5)

        self.retirement_tips_button = ctk.CTkButton(button_frame, text="Get Retirement Tips", command=self.get_retirement_tips, width=150)
        self.retirement_tips_button.grid(row=0, column=3, padx=5, pady=5)

        self.reset_conversation_button = ctk.CTkButton(button_frame, text="Reset Conversation", command=self.reset_conversation, width=150)
        self.reset_conversation_button.grid(row=0, column=4, padx=5, pady=5)

    def display_ai_response(self, response):
        """Helper function to display the AI response in the text box."""
        self.ai_text_box.delete(1.0, tk.END)  # Clear previous response
        if response:
            self.ai_text_box.insert(tk.END, response)
        else:
            self.ai_text_box.insert(tk.END, "Unable to fetch a response. Please try again.")

    def get_budget_tips(self):
        """Fetch budget tips from the AI and display them."""
        prompt = "Provide tips for managing a budget effectively."
        response = self.ai_chat.generate_response(prompt)
        self.display_ai_response(response)

    def get_savings_tips(self):
        """Fetch savings tips from the AI and display them."""
        prompt = "Provide tips for effective savings strategies."
        response = self.ai_chat.generate_response(prompt)
        self.display_ai_response(response)

    def get_investment_tips(self):
        """Fetch investment tips from the AI and display them."""
        prompt = "Can you suggest some low-risk investment strategies to grow savings over time?"
        response = self.ai_chat.generate_response(prompt)
        self.display_ai_response(response)

    def get_retirement_tips(self):
        """Fetch retirement planning tips from the AI and display them."""
        prompt = "Can you provide some tips on preparing for retirement effectively?"
        response = self.ai_chat.generate_response(prompt)
        self.display_ai_response(response)

    def reset_conversation(self):
        """Reset the AI conversation box."""
        self.ai_text_box.delete(1.0, tk.END)
        self.ai_text_box.insert(tk.END, "Conversation reset. Ask me anything about budgeting, savings, investments, or retirement.")






    def create_export_section(self):
        """Create export buttons for CSV and JSON."""
        self.export_csv_button = ctk.CTkButton(self, text="Export Data to CSV", command=self.export_to_csv)
        self.export_csv_button.grid(row=11, column=0, padx=10, pady=10)

        self.export_json_button = ctk.CTkButton(self, text="Export Data to JSON", command=self.export_to_json)
        self.export_json_button.grid(row=11, column=1, padx=10, pady=10)

    def export_to_csv(self):
        """Export financial data to CSV format."""
        try:
            income_data = pd.DataFrame(list(self.budget_manager.incomes.items()), columns=['Income Source', 'Amount'])
            expense_data = [
                {"Category": category, "Name": name, "Amount": amount}
                for category, expenses in self.budget_manager.expenses.items()
                for name, amount in expenses.items()
            ]
            expense_df = pd.DataFrame(expense_data)
            income_data.to_csv("income_data.csv", index=False)
            expense_df.to_csv("expense_data.csv", index=False)
            self.output_label.configure(text="Data exported to CSV files: income_data.csv, expense_data.csv")
        except Exception as e:
            self.output_label.configure(text=f"Error exporting to CSV: {e}")

    def export_to_json(self):
        """Export financial data to JSON format."""
        try:
            data = {
                "incomes": self.budget_manager.incomes,
                "expenses": self.budget_manager.expenses,
                "bills": self.budget_manager.bills,
                "investments": self.budget_manager.investments,
                "debts": self.budget_manager.debts,
                "financial_goals": self.budget_manager.financial_goals,
            }
            with open("budget_data.json", "w") as file:
                json.dump(data, file, indent=4)
            self.output_label.configure(text="Data exported to budget_data.json")
        except Exception as e:
            self.output_label.configure(text=f"Error exporting to JSON: {e}")

    # def get_budget_tips(self):
    #     """Generate AI tips for budgeting based on current financial data."""
    #     prompt = (
    #         f"My current monthly income is ${sum(self.budget_manager.incomes.values()):.2f} "
    #         f"and my total expenses are ${sum(sum(exp.values()) for exp in self.budget_manager.expenses.values()):.2f}. "
    #         "Can you suggest some tips for better budgeting?"
    #     )
    #     response = self.ai_chat.generate_response(prompt)
    #     self.ai_response_label.configure(text=response)

    # def get_savings_tips(self):
    #     """Generate AI tips for savings based on current financial data."""
    #     prompt = (
    #         f"I save approximately ${self.budget_manager.calculate_monthly_savings():.2f} monthly. "
    #         "Can you suggest ways to increase my savings rate?"
    #     )
    #     response = self.ai_chat.generate_response(prompt)
    #     self.ai_response_label.configure(text=response)

    # def get_investment_tips(self):
    #     """Generate AI tips for investments based on current financial data."""
    #     prompt = (
    #         "Based on my current income and expenses, can you suggest some low-risk investment strategies "
    #         "to grow my savings over time?"
    #     )
    #     response = self.ai_chat.generate_response(prompt)
    #     self.ai_response_label.configure(text=response)

    # def get_retirement_tips(self):
    #     """Generate AI tips for retirement planning based on current financial data."""
    #     prompt = (
    #         f"I am currently {self.budget_manager.age} years old and wish to retire at 65. "
    #         "Can you provide some tips on how to better prepare for retirement?"
    #     )
    #     response = self.ai_chat.generate_response(prompt)
    #     self.ai_response_label.configure(text=response)

    # def reset_conversation(self):
    #     """Reset the AI conversation."""
    #     self.ai_chat.reset_conversation()
    #     self.ai_response_label.configure(text="Conversation reset.")


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

    def calculate_monthly_savings(self):
        """Calculates and returns the monthly savings."""
        total_expenses = sum(sum(exp.values()) for exp in self.expenses.values())
        total_bills = sum(self.bills.values())
        total_debt_payments = sum(debt["monthly_payment"] for debt in self.debts.values())
        self.savings = self.monthly_income - (total_expenses + total_bills + total_debt_payments)
        return self.savings

    def add_goal(self, name, target_amount):
        """Add a financial goal with a target amount."""
        self.financial_goals[name] = {"target_amount": target_amount, "current_amount": 0}

    def contribute_to_goal(self, name, amount):
        """Contribute a specified amount to a financial goal."""
        if name in self.financial_goals:
            self.financial_goals[name]["current_amount"] += amount
        else:
            print(f"Goal '{name}' not found.")

if __name__ == "__main__":
    # Create BudgetManager instance with default parameters
    budget_manager = BudgetManager(age=29, annual_income=82000)
    budget_manager_two = BudgetManager(age=29, annual_income=52000)
    # Launch the GUI with the budget manager instance
    app = BudgetManagerGUI(budget_manager)
    app.mainloop()
