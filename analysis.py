# analysis.py
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import defaultdict
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database import fetch_all_transactions


def fetch_data():
    """Fetch and process all transaction data."""
    data = fetch_all_transactions()
    income = expense = 0
    income_totals = defaultdict(float)
    expense_totals = defaultdict(float)

    for row in data:
        try:
            trans_type = row[1]
            amount = float(row[2])
            category = row[4] or "Uncategorized"

            if trans_type == 'Income':
                income += amount
                income_totals[category] += amount 
            elif trans_type == 'Expense':
                expense += amount
                expense_totals[category] += amount
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    return income, expense, income_totals, expense_totals



def create_analysis_plot(income, expense, income_totals, expense_totals):
    """Create the charts and plots for analysis."""
    sns.set_theme(style="whitegrid", palette="deep", font_scale=1.2)
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    fig.subplots_adjust(hspace=0.4, wspace=0.3)

    # Pie Chart: Income vs Expense
    # Donut Chart: Income Overview
    income_categories = list(income_totals.keys())
    income_amounts = list(income_totals.values())

    wedges, texts, autotexts = axs[0, 0].pie(income_amounts,
                                         autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
                                         startangle=90,
                                         pctdistance=1.15,
                                         colors=sns.color_palette("Set1", len(income_categories)),
                                         wedgeprops={'linewidth': 1.5, 'edgecolor': 'white', 'width': 0.6})
    axs[0, 0].set_title("Income Overview", fontsize=16, fontweight='bold')
    axs[0, 0].text(0, 0, f"₹{income:.0f}", ha='center', va='center', fontsize=14, fontweight='bold')

    for text in texts + autotexts:
        text.set_fontsize(10)

    # Add legend
    legend_patches = [Patch(facecolor=col, edgecolor='white', label=cat)
                  for col, cat in zip(sns.color_palette("Set1", len(income_categories)), income_categories)]
    axs[0, 0].legend(handles=legend_patches,
                 title="Categories",
                 bbox_to_anchor=(1.05, 1),
                 loc='upper left',
                 borderaxespad=0.,
                 fontsize=9,
                 title_fontsize=10)


    # Donut Chart: Expense Overview
    categories = list(expense_totals.keys())
    amounts = list(expense_totals.values())
    wedges, texts, autotexts = axs[1, 0].pie(amounts,
                                              autopct=lambda pct: f'{pct:.1f}%' if pct > 3 else '',
                                              startangle=90,
                                              pctdistance=1.15,
                                              colors=sns.color_palette("Set1", len(categories)),
                                              wedgeprops={'linewidth': 1.5, 'edgecolor': 'white', 'width': 0.6})
    axs[1, 0].set_title("Expense Overview", fontsize=16, fontweight='bold')
    axs[1, 0].text(0, 0, f"₹{expense:.0f}", ha='center', va='center', fontsize=14, fontweight='bold')

    for text in texts + autotexts:
        text.set_fontsize(11)

    # Add legends for Donut Chart
    category_colors = sns.color_palette("Set1", len(categories))
    legend_patches = [Patch(facecolor=col, edgecolor='white', label=cat)
                      for col, cat in zip(category_colors, categories)]
    axs[1, 0].legend(handles=legend_patches,
                     title="Categories",
                     bbox_to_anchor=(1.05, 1),
                     loc='upper left',
                     borderaxespad=0.,
                     fontsize=9,
                     title_fontsize=10)

    # Bar Chart: Expenses by Category
    bars = axs[0, 1].bar(categories, amounts, color=sns.color_palette("tab10", len(categories)))
    axs[0, 1].set_title("Expenses by Category", fontsize=12, fontweight='bold')
    axs[0, 1].set_ylabel("Amount (₹)", fontsize=9)
    axs[0, 1].tick_params(axis='x', labelbottom=False)
    axs[0, 1].grid(axis='y', linestyle='--', alpha=0.4)

    # Display values on top of bars
    for bar, amount in zip(bars, amounts):
        height = bar.get_height()
        axs[0, 1].annotate(f"₹{amount:,.0f}",
                           xy=(bar.get_x() + bar.get_width() / 2, height),
                           xytext=(0, 4),
                           textcoords="offset points",
                           ha='center', va='bottom',
                           fontsize=8, color='black')

    # Add legends for Bar Chart
    categories_colors = sns.color_palette("Set1", len(categories))
    bars_legend = [Patch(facecolor=col, edgecolor='white', label=cat)
                   for col, cat in zip(categories_colors, categories)]
    axs[0, 1].legend(handles=bars_legend,
                     title="Categories",
                     bbox_to_anchor=(1.02, 1),
                     loc='upper left',
                     borderaxespad=0.,
                     fontsize=9,
                     title_fontsize=10)

    return fig


def embed_plot_into_tk(fig, window):
    """Embed the created plot into Tkinter window."""
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)
