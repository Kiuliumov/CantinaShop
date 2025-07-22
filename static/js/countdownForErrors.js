const countdown = document.getElementById('countdown');
    let seconds = parseInt(countdown.innerText);

    const timer = setInterval(() => {
      if (seconds <= 1) {
        clearInterval(timer);
        window.location.href = window.redirectUrl
      } else {
        seconds -= 1;
        countdown.innerText = seconds;
      }
    }, 1000);