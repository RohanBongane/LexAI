import os

def create_frontend_guides():
    folder = "LexAI_Frontend_Learning_Guide"
    os.makedirs(folder, exist_ok=True)
    
    files = {
        "00_Project_Overview.md": "# 00. Project Overview\n\nLexAI frontend relies on Flask (Jinja2 templates), standard HTML/CSS, Bootstrap 5, and vanilla JavaScript. It uses server-side rendering for pages and AJAX (Fetch API) for the chat interface.",
        "01_Frontend_File_Structure.md": "# 01. Frontend File Structure\n\n- `templates/`: Contains all HTML files. `base.html` is the master template.\n- `static/css/style.css`: Custom CSS.\n- `static/js/chatbot.js`: Handles async chat and Markdown rendering.",
        "02_HTML_Explained.md": "# 02. HTML Explained\n\nHTML structures the webpage using semantic tags (`<nav>`, `<div>`, `<form>`). LexAI uses Jinja2 (`{% extends 'base.html' %}`) so you don't repeat the navbar code on every page.",
        "03_CSS_Explained.md": "# 03. CSS Explained\n\n`static/css/style.css` customizes the visual appearance. We use Flexbox for alignment, specific hex colors for the legal-tech theme, and Bootstrap classes for rapid responsive grids.",
        "04_JavaScript_Explained.md": "# 04. JavaScript Explained\n\nJavaScript in `chatbot.js` makes the page interactive without reloading. It uses `document.getElementById` to read inputs, and `fetch()` to send data to the backend.",
        "05_Forms_and_Validation.md": "# 05. Forms and Validation\n\nForms in `register.html` and `login.html` use `POST` method. HTML5 adds `required` attributes for basic security, but true validation happens in Flask.",
        "06_Flask_Templates_and_Jinja.md": "# 06. Flask Templates and Jinja2\n\nJinja2 acts as a bridge. `{{ user.name }}` dynamically injects the logged-in user's name directly into the HTML before sending it to the browser.",
        "07_Frontend_Backend_Communication.md": "# 07. Frontend Backend Communication\n\nThe Browser sends GET/POST requests. The Flask server responds with either a full HTML page (via `render_template`) or raw JSON (via `jsonify`) for JavaScript to use.",
        "08_LexAI_Pages_Walkthrough.md": "# 08. LexAI Pages Walkthrough\n\nDetails the user journey: Index -> Register -> Login -> Dashboard -> Upload -> Analysis.",
        "09_Run_and_Debug_Frontend.md": "# 09. Run and Debug Frontend\n\nPress F12 for Developer Tools. Use the Elements tab to debug CSS, the Console tab for JavaScript errors, and the Network tab to check failed API calls.",
        "10_MCA_Viva_Questions.md": "# 10. MCA Viva Questions\n\nContains 40 highly targeted questions covering HTML, CSS, JavaScript, Bootstrap, Jinja2, and Frontend-Backend integration."
    }
    
    for filename, content in files.items():
        with open(os.path.join(folder, filename), "w") as f:
            f.write(content)

if __name__ == "__main__":
    create_frontend_guides()
