import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

file_path = 'DataScience_salaries_US.csv'
data = pd.read_csv(file_path)

job_title_counts = data['job_title'].value_counts()
experience_level_counts = data['experience_level'].value_counts()

available_job_titles = job_title_counts[job_title_counts >= 100].index
available_experience_levels = experience_level_counts[experience_level_counts >= 100].index

remote_ratio_mapping = {0: 'Non remote', 50: 'Hybrid', 100: 'Full remote'}
data['remote_category'] = data['remote_ratio'].map(remote_ratio_mapping)

st.title("Salary Simulation")

st.sidebar.header("User Inputs")
job_title = st.sidebar.selectbox("Select Job Title", available_job_titles)
experience_level = st.sidebar.selectbox("Select Experience Level", available_experience_levels)
remote_category = st.sidebar.selectbox("Select Remote Category", ['non remote', 'hybrid', 'full remote'])
n_simulations = st.sidebar.number_input("Number of Simulations", min_value=100, max_value=10000, value=1000)

# Simulation function with caching
@st.cache_data
def salary_simulation(job_title, experience_level, remote_category, n_simulations):
    filtered_data = data[
        (data['job_title'] == job_title) &
        (data['experience_level'] == experience_level) &
        (data['remote_category'] == remote_category)
    ]

    if filtered_data.empty:
        return None

    salary_data = filtered_data['salary']
    simulated_salaries = np.random.choice(salary_data, size=n_simulations, replace=True)
    mean_salary = np.mean(simulated_salaries)
    median_salary = np.median(simulated_salaries)
    salary_95ci = np.percentile(simulated_salaries, [2.5, 97.5])

    return simulated_salaries, mean_salary, median_salary, salary_95ci

# Run the simulation
if st.sidebar.button("Run Simulation"):
    with st.spinner('Running simulation...'):
        result = salary_simulation(job_title, experience_level, remote_category, n_simulations)
        if result:
            simulated_salaries, mean_salary, median_salary, salary_95ci = result
            
            # Display results
            st.subheader(f"Results for {job_title} ({experience_level}):")
            st.write(f"Mean Salary: ${mean_salary:,.2f}")
            st.write(f"Median Salary: ${median_salary:,.2f}")
            st.write(f"95% Confidence Interval: ${salary_95ci[0]:,.2f} - ${salary_95ci[1]:,.2f}")

            # Plot the histogram
            st.subheader("Simulation Histogram")
            fig, ax = plt.subplots()
            sns.histplot(simulated_salaries, bins=30, kde=True, ax=ax, color='blue')
            ax.axvline(mean_salary, color='red', linestyle='dashed', linewidth=1, label=f"Mean: ${mean_salary:,.2f}")
            ax.axvline(median_salary, color='green', linestyle='dashed', linewidth=1, label=f"Median: ${median_salary:,.2f}")
            ax.set_title("Salary Distribution")
            ax.set_xlabel("Salary")
            ax.set_ylabel("Frequency")
            ax.legend()
            st.pyplot(fig)

            # Plot the box plot
            st.subheader("Salary Distribution Box Plot")
            fig, ax = plt.subplots()
            sns.boxplot(x=simulated_salaries, ax=ax, color='blue')
            ax.set_title("Salary Distribution")
            ax.set_xlabel("Salary")
            st.pyplot(fig)
        else:
            st.warning("No data available for the selected parameters.")
