from flask import Flask, render_template_string, Response
import requests, random, threading, time

app = Flask(__name__)

# URL of the special image
special_meme_url = "https://i.redd.it/almo0i9x30id1.jpeg"

# Global variables to store the current meme URL, next update time, and page color
current_meme_url = None
next_update_time = None
current_color = "#f0f8ff"

# Function to fetch a random meme from Reddit
def get_random_meme():
    url = "https://www.reddit.com/r/ProgrammerHumor//top.json?limit=50"
    headers = {'User-agent': 'your bot 0.1'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        memes = response.json()["data"]["children"]
        meme = random.choice(memes)["data"]
        return meme["url"]
    else:
        return None

# Function to get a random color
def get_random_color():
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))

def update_meme():
    global current_meme_url, next_update_time, current_color
    counter = 0
    while True:
        counter += 1
        if counter % 5 == 0:
            current_meme_url = special_meme_url
        else:
            current_meme_url = get_random_meme()
            if not current_meme_url:
                current_meme_url = "https://i.imgur.com/Y2aFQKe.jpg"  # Fallback meme if Reddit API fails
        
        next_update_time = time.time() + 30  # Set next update time
        current_color = get_random_color()  # Get a new color
        time.sleep(30)

@app.route('/')
def home():
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Random Reddit Meme Generator</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: {{ bg_color }};
                    color: #333;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                .container {
                    text-align: center;
                    padding: 10px;
                    border: 2px solid #000;
                    border-radius: 10px;
                    background-color: #fff;
                    box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
                    width: 90vw;
                    max-width: 600px;
                    position: relative;
                    z-index: 1;
                }
                h1 {
                    font-size: 1.5em;
                    margin-bottom: 15px;
                }
                img {
                    width: 100%;
                    height: auto;
                    border-radius: 10px;
                    margin-bottom: 15px;
                }
                #timer {
                    font-size: 1.2em;
                    margin-top: 10px;
                }
                .confetti {
                    position: absolute;
                    width: 10px;
                    height: 10px;
                    background-color: red;
                    border-radius: 50%;
                    top: -10px;
                    animation: fall 3s infinite;
                }
                .confetti::after {
                    content: '★';
                    color: white;
                    position: absolute;
                    font-size: 8px;
                    left: 0;
                    top: -4px;
                    text-align: center;
                    width: 100%;
                }
                @keyframes fall {
                    to {
                        transform: translateY(100vh) rotate(360deg);
                    }
                }
                #credits {
                    font-size: 1em;
                    margin-top: 20px;
                }
            </style>
            <script>
                const eventSource = new EventSource("/stream");
                let nextUpdateTime = 0;

                eventSource.onmessage = function(event) {
                    const data = event.data.split(',');
                    document.getElementById("memeImage").src = data[0];
                    nextUpdateTime = parseFloat(data[1]) * 1000; // Convert to milliseconds
                    document.body.style.backgroundColor = data[2]; // Set new background color
                };

                function updateCountdown() {
                    const now = Date.now();
                    const timeLeft = nextUpdateTime - now;
                    if (timeLeft <= 0) {
                        document.getElementById("timer").innerHTML = "Updating...";
                        return;
                    }
                    const seconds = Math.ceil(timeLeft / 1000);
                    document.getElementById("timer").innerHTML = "New meme in " + seconds + " seconds";
                }

                setInterval(updateCountdown, 1000); // Update countdown every second

                function createConfetti() {
                    const confettiCount = 100;
                    for (let i = 0; i < confettiCount; i++) {
                        let confetti = document.createElement('div');
                        confetti.className = 'confetti';
                        confetti.style.left = Math.random() * 100 + 'vw';
                        confetti.style.animationDelay = Math.random() * 3 + 's';
                        document.body.appendChild(confetti);
                    }
                }

                createConfetti();  // Confetti effect always
            </script>
        </head>
        <body>
            <div class="container">
                <h1>Random Reddit Meme!</h1>
                <img id="memeImage" src="{{ meme_url }}" alt="Random Meme">
                <div id="timer">New meme in 30 seconds</div>
                <div id="credits">Credits: Ozan Kaygusuz</div>
            </div>
        </body>
        </html>
    ''', meme_url=current_meme_url, bg_color=current_color)

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            yield f"data: {current_meme_url},{next_update_time},{current_color}\n\n"
            time.sleep(1)  # Send updates every second

    return Response(event_stream(), content_type='text/event-stream')


if __name__ == '__main__':
    # Start the background thread to update the meme every 30 seconds
    threading.Thread(target=update_meme, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=True)
