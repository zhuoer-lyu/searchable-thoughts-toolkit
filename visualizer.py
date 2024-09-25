#this one takes in level 1, 2a, or 2b writing sessions + writing outcomes and outputs graphs

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from datetime import datetime, timedelta
import json

##### Writing process visualization - Gantt Chart #####

def create_action_df(actions_by_session, users_included):
    actions_list = []
    for user in users_included:
        if user not in actions_by_session:  # Check if user data exists
            print(f"Warning: No data found for {user}")
            continue  # Skip to the next user
        actions_user = actions_by_session[user]
        actions_user = pd.DataFrame.from_dict(actions_user)
        actions_user['user_id'] = user
        actions_list.append(actions_user)

    # Check if actions_list is empty
    if not actions_list:
        return pd.DataFrame()  # Return an empty DataFrame

    actions = pd.concat(actions_list).reset_index()
    return actions

def action_plot(actions_by_session, users_included, action_types_included, y_order=None, include_outcome_measure=False):    
    actions = create_action_df(actions_by_session, users_included)

    # Check if the DataFrame is empty
    if actions.empty:
        print(f"No data to plot for users {users_included}")
        return  # Skip this pair if no data

    actions_included = actions[actions['action_type'].isin(action_types_included)].reset_index()

    # Adjust the scale factor to stretch the index values on the x-axis over a longer period.
    # The current set up is intended to represent a writing session of about 30 minutes. 
    scale_factor = 7  # Each index step will represent 7 seconds
    # Scale the index and end_index values to extend the timeline.
    actions_included['index'] = actions_included['index'].apply(lambda x: x * scale_factor)
    actions_included['end_index'] = actions_included['index'].apply(lambda x: x + 60)  # Each action lasts 60 seconds.

    # Convert index and end_index from seconds relative to a base date
    base_date = datetime(2024, 1, 1)
    actions_included['index'] = actions_included['index'].apply(lambda x: base_date + timedelta(seconds=x))
    actions_included['end_index'] = actions_included['end_index'].apply(lambda x: base_date + timedelta(seconds=x))

    # Define a consistent color mapping
    color_map = {
        'reject_suggestion': '#ffb8a2',
        'minor_insert_mindless_edit': '#359ae8',
        'major_insert_mindless_echo': '#0aae9b',
        'accept_suggestion': '#ffab40',
        'writer_topic_shift': '#a2a82c',
        'AI_led_topic_shift': '#b4a7d6'
    }

    for user in users_included:
        # Create the Plotly timeline figure
        actions_included_user = actions_included[actions_included['user_id'] == user]
        fig = px.timeline(actions_included_user,
                          x_start="index",
                          x_end="end_index",
                          y="action_type",
                          color="action_type",
                          category_orders={"action_type": y_order},
                          color_discrete_map=color_map)

        # Set a fixed height based on the number of action types
        bar_height = 48  # Set a fixed height per category
        fig.update_layout(
            title=f"User {user.split('_')[1]}",
            height=bar_height * len(y_order),  # Multiply by the number of action types
            width=1200,  # Set plot width
            bargap=0.4,  # Set gap between bars
            plot_bgcolor='white' # Set background as white
        )

        fig.show()

    # Plot the outcome measure using Matplotlib, if specified
    if include_outcome_measure:
        plt.figure(figsize=(14, 6))
        sns.lineplot(data=actions_included, x='index', y=include_outcome_measure, hue='user_id')
        plt.title(f'Outcome Measure: {include_outcome_measure}')
        plt.xlabel('Time')
        plt.ylabel(include_outcome_measure)
        plt.show()

### Example usage ###

# # Select actions types to include:
# action_types_included = ['reject_suggestion',
#                          'minor_insert_mindless_edit',
#                          'major_insert_mindless_echo',
#                          'accept_suggestion', 
#                          'writer_topic_shift', 
#                          'AI_led_topic_shift']

# # Select users to include:
# # get_pairs = [('user_' + str(num) + 'a', 'user_' + str(num) + 'b') for num in range(1, 17)] # Get writing sessions for users 1-16
# get_pairs = [('user_5a', 'user_5b')] # Get writing sessions for user 5 only

# # Load raw writing log file:
# with open('actions_with_mindless_echo_and_edit_and_alignment_STUDY_1.json') as f:
#     actions_by_session_full_s1 = json.load(f)

# # Generate plots:
# for pair in get_pairs:
#     action_plot(actions_by_session_full_s1, pair, action_types_included,
#                 y_order=action_types_included,
#                 include_outcome_measure=False)
