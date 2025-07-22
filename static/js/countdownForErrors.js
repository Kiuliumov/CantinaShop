const countdown = document.getElementById('countdown');
    let seconds = parseInt(countdown.innerText);

    const timer = setInterval(() => {
      if (seconds <= 1) {
        window.location.href = window.redirectUrl;
        clearInterval(timer);
      } else {
        seconds -= 1;
        countdown.innerText = seconds;
      }
    }, 1000);