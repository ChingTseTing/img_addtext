from flask_app import app

#主程式
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False,host='0.0.0.0', port=port)
