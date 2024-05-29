from website import init_app
# import crawler
# import consumer
# from concurrent.futures import ThreadPoolExecutor


if __name__ == '__main__':
    app = init_app()
    app.run(debug=True)