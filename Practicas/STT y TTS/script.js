function listen() {
  let inputArea = document.getElementById('input-area');
  let outputArea = document.getElementById('output-area');

  // Inicializamos el reconocimiento de voz
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  var recognition = new SpeechRecognition();
  
  // Cambiamos el idioma a Español (México)
  recognition.lang = "es-MX";
  recognition.start();

  recognition.onresult = function(event) {
    // Convertimos todo a minúsculas para que sea más fácil de comparar
    let transcript = event.results[0][0].transcript.toLowerCase();
    console.log("Trans: ", transcript);

    // Si la frase que dijiste incluye la palabra "hora"
    if (transcript.includes("hora")) {
      let fechaActual = new Date();
      
      // Formateamos la hora para que suene natural (ej. "3:15 PM")
      let opcionesHora = { hour: 'numeric', minute: 'numeric', hour12: true };
      let horaEnTexto = fechaActual.toLocaleTimeString('es-MX', opcionesHora);
      let mensaje = "Son las " + horaEnTexto + " mi amor";
      
      outputArea.innerHTML = mensaje;
      hablar(mensaje); // Llamamos a la función que sintetiza la voz

    } else if (transcript.includes("hola")) {
      outputArea.innerHTML = "¡Hola, mi amor!";
      hablar("¡Hola, mi amor!");
    } else {
      outputArea.innerHTML = "No entendí la instrucción.";
    }
  }
}

// Función adicional para que el navegador hable
function hablar(texto) {
  if ('speechSynthesis' in window) {
    let utterance = new SpeechSynthesisUtterance(texto);
    utterance.lang = 'es-MX'; // Configuramos el acento en Español (México)
    
    // Opcional: puedes ajustar la velocidad o el tono
    // utterance.rate = 1; // Velocidad normal
    // utterance.pitch = 1; // Tono normal

    window.speechSynthesis.speak(utterance);
  } else {
    console.warn("La síntesis de voz no está soportada en este navegador.");
  }
}
