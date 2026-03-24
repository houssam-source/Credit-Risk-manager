import streamlit as st

class MultiPage: 
    """
    Class for generating multiple pages using Streamlit
    """
    def __init__(self):
        self.pages = []
    
    def add_page(self, title, func):
        """
        Add a page to the list of pages
        
        Args:
            title (str): Title of the page
            func: Function to run when the page is selected
        """
        self.pages.append({"title": title, "function": func})

    def run(self):
        # Dropdown menu for page selection
        page = st.sidebar.selectbox(
            'Navigate to',
            self.pages, 
            format_func=lambda page: page['title']
        )

        # Run the selected page function
        page['function']()