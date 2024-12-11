# Realtor's Housing Price Prediction App - Canada

This repository hosts the development of a real estate price prediction app for realtors in Canada. The app scrapes weekly housing data from **Kijiji** and uses machine learning to predict prices for the upcoming week. It notifies realtors when listings are undervalued and, in the future, will provide recommendations on how to increase property value through potential improvements.

## Features
- **Weekly Data Updates**: Kijiji listings are scraped weekly and added to our dataset.
- **Price Predictions**: Uses machine learning to predict housing prices for the coming week.
- **Real-time Alerts**: Notifies realtors about listings priced lower than predicted.
- **Future Improvements**:
  - Recommendations for modifications to enhance property value.
  - Insights into market trends and property features that affect pricing.

## Dataset Overview
The dataset includes:
- Listing price
- Location (city, postal code)
- Property size (sq ft)
- Number of bedrooms and bathrooms
- Property age and additional features (garage, garden, etc.)

Weekly updates ensure that the model stays current with the latest market trends.


# Housing Price Prediction for Realtors

## Project Overview
This project aims to provide real-time housing price predictions specifically designed for realtors. By scraping updated data weekly from prominent real estate websites like Kijiji and Realtor.ca, the project utilizes advanced data processing techniques and predictive modeling to offer actionable insights to realtors. The project's backbone consists of Python for data manipulation, MongoDB for data storage, and AWS cloud services for hosting the application and managing workflows.

## Key Features
- **Dynamic Data Scraping:** Automated scraping of housing listings from Kijiji and Realtor.ca, ensuring fresh and relevant data is always available.
- **Robust Data Processing:** Utilization of sophisticated Python libraries to clean and transform raw data into a structured format suitable for analysis.
- **Persistent Data Storage:** MongoDB is used for its flexibility and performance in handling large datasets, which is crucial for real-time applications.
- **Automated Workflow:** Airflow on AWS EC2 automates the entire data pipeline, from scraping to data storage and running predictive models.
- **Real-time Notifications:** Integration with Twilio to send automated notifications to subscribed users, providing them with the latest insights on housing price trends and predictions.
- **Advanced Predictive Analytics:** The XGBoost algorithm is employed to determine influential factors in housing prices, offering a granular view of what drives market changes.

## System Architecture
![System Architecture](link-to-your-system-architecture-diagram.png)
This diagram provides a visual representation of the data flow and component interaction within the project, from data acquisition to user notification.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Python 3.8 or higher
- MongoDB Community Edition
- AWS CLI configured with Administrator access
- Twilio account with API credentials

### Installation
1. **Clone the Repository:**

### Setup
1. **MongoDB:**
- Ensure MongoDB is running on your local machine or a dedicated server.
- Use the provided schema files to set up your databases and collections.
2. **AWS Configuration:**
- Set up an EC2 instance to host the Airflow server.
- Configure the security groups and network settings to allow appropriate access.
3. **Twilio Configuration:**
- Enter your Twilio credentials in `twilio_config.json` to set up SMS notifications.

### Running the Application
1. **Start the Airflow server on EC2:**

2. **Trigger the DAG:**
- Manually trigger the DAG from the Airflow Web UI to start the pipeline.
3. **Access the Frontend:**
- Navigate to `https://housing-nextjs-ui.vercel.app/` to view the predictions and trends.

## Contributing
Interested in contributing? We love pull requests! Here's how you can contribute:
- Fork the repository
- Create a new branch (`git checkout -b feature-branch`)
- Commit your changes (`git commit -am 'Add some feature'`)
- Push to the branch (`git push origin feature-branch`)
- Open a new Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE) file for details.

## Acknowledgments
- Thanks to Kijiji and Realtor.ca for the data that powers this project.
- AWS for the robust cloud infrastructure.
- Twilio for enhancing user engagement through timely notifications.



