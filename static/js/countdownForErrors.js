const countdown = document.getElementById('countdown');
    const redirectUrl = "{% url 'index' %}"
    let seconds = parseInt(countdown.innerText);

    const timer = setInterval(() => {
      if (seconds <= 1) {
        clearInterval(timer);
        window.location.href = redirectUrl;
      } else {
        seconds -= 1;
        countdown.innerText = seconds;
      }
    }, 1000);