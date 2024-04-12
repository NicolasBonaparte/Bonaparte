const apiKey = '4ecdb8c869f3428792ca4168b70fdcb8';
const loadedGames = new Set(); // Conjunto para almacenar juegos cargados
var app;

function getDates() {
  const today = new Date();
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(today.getDate() - 30);

  return {
    currentDate: today.toISOString().split('T')[0],
    thirtyDaysAgoDate: thirtyDaysAgo.toISOString().split('T')[0],
  };
}

//Api cheapshark
 async function updateCardWithCheapShark(card, game) {
  try {
      const cheapSharkApiUrl = `https://www.cheapshark.com/api/1.0/games?title=${encodeURIComponent(game.name)}`;
      const response = await fetch(cheapSharkApiUrl);
      const cheapSharkData = await response.json();

      if (cheapSharkData && cheapSharkData.length > 0) {
          const cheapestPrice = cheapSharkData[0].cheapest;
          const cardPrice = card.querySelector('.card-price');
          cardPrice.textContent = `$${cheapestPrice}`;
      } else {
          const cardPrice = card.querySelector('.card-price');
          cardPrice.textContent = 'No hay ofertas';
      }
      const cardDescription = card.querySelector('.card-text');
      cardDescription.textContent = game.description;
  } catch (error) {
      console.error('Error al cargar los datos de CheapShark:', error);
  }
}

 // Función para cambiar el juego actual
 function cambiarJuego(nuevoJuego) {
  // Lógica para cambiar el juego actual

  // Actualizar los botones con la nueva información del juego
  const verPaginaButton = document.getElementById('verPaginaButton');
  verPaginaButton.setAttribute('data-store', nuevoJuego.store);
  verPaginaButton.setAttribute('data-game-id', nuevoJuego.id);
  verPaginaButton.setAttribute('data-game-name', nuevoJuego.name); // Agrega el nombre del juego al atributo de datos
}

async function loadAndRenderCategoryGames(categoryUrl, cardsSelector) {
  const cards = document.querySelectorAll(cardsSelector);

  try {
    const response = await fetch(categoryUrl);
    const data = await response.json();
    const games = data.results.filter(game => !loadedGames.has(game.id)); // Filtrar juegos no cargados

    for (let i = 0; i < cards.length && i < games.length; i++) {
      const card = cards[i];
      const game = games[i];

      loadedGames.add(game.id); // Agregar el juego al conjunto de juegos cargados

      const cardTitle = card.querySelector('.card-title');
      cardTitle.textContent = game.name;

      const cardDescription = card.querySelector('.card-text');
      cardDescription.textContent = game.description;

      const cardImage = card.querySelector('.card-img-top');
      cardImage.src = game.background_image;

      await updateCardWithCheapShark(card, game);
    }
  } catch (error) {
    console.error(`Error al cargar los datos de juegos de la categoría ${cardsSelector}:`, error);
  }
}

async function loadFeaturedGames() {
  const dates = getDates();
  const featuredUrl = `https://api.rawg.io/api/games?key=${apiKey}&dates=${dates.thirtyDaysAgoDate},${dates.currentDate}`;

  try {
    const response = await fetch(featuredUrl);
    const data = await response.json();
    const games = data.results.filter(game => !loadedGames.has(game.id));

    const cards = document.querySelectorAll('.card');
    for (let i = 0; i < cards.length && i < games.length; i++) {
      const card = cards[i];
      const game = games[i];

      loadedGames.add(game.id);

      const cardTitle = card.querySelector('.card-title');
      cardTitle.textContent = game.name;

      const cardImage = card.querySelector('.card-img-top');
      cardImage.src = game.background_image;

      const verPaginaButton = card.querySelector('.btn-info');

      // Verifica si el botón existe antes de intentar modificarlo
      if (verPaginaButton) {
     
        verPaginaButton.setAttribute('data-game-id', game.id);
        verPaginaButton.setAttribute('data-game-name', game.name);

        const cardDescription = card.querySelector('.card-text');
        cardDescription.textContent = game.description;

        // Agregar evento de clic al botón
        verPaginaButton.addEventListener('click', redirigirAPagina);

        await updateCardWithCheapShark(card, game);
      }
    }
  } catch (error) {
    console.error('Error al cargar los datos de juegos destacados:', error);
  }
}

// Función para manejar el clic en el botón y redirigir a la oferta
function redirigirAPagina(event) {
  try {
    // Obtener la tienda o plataforma del juego desde el atributo data-store
    const store = this.getAttribute('data-store').toLowerCase();

    // Obtener el ID del juego desde el atributo data-game-id
    const gameId = this.getAttribute('data-game-id');

    // Redirigir a la URL de la tienda correspondiente, pero directamente a la oferta del juego
    if (store === 'steam') {
      window.location.href = `https://store.steampowered.com/app/${encodeURIComponent(gameId)}/?utm_source=your_website&utm_medium=button&utm_campaign=game_offer`;
    } else if (store === 'epic') {
      window.location.href = `https://www.epicgames.com/store/es-ES/p/${encodeURIComponent(gameId)}/?utm_source=your_website&utm_medium=button&utm_campaign=game_offer`;
    } else {
      console.error(`Tienda no compatible: ${store}`);
    }
  } catch (error) {
    console.error('Error al redirigir a la página del juego:', error);
  }
}