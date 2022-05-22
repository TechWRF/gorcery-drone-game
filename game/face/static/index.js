import GameView from "./js/GameView.js";

const navigateTo = url => {
  // fires popstate event
  history.pushState({}, '', url);
  router();
};

const router = async () => {
  const routes = [
    {path: "/", view: GameView},
    // {path: "/drones", view: () => console.log("Viewing Drones")},
    // {path: "/settings", view: () => console.log("Viewing Settings")}
  ]

  const potentialMatches = routes.map(route => {
    return {
      route: route,
      isMatch: location.pathname === route.path
    };
  });

  let match = potentialMatches.find(potentialMatch => potentialMatch.isMatch);

  // possible to define 404 message page here or return to main page
  if (!match) {
    match = {
      route: routes[0],
      isMatch: true
    };
  };

  // create selected page view instance
  const view = new match.route.view();

  // inject html from matched route view class
  document.querySelector("#app").innerHTML = await view.getHtml();

  // console.log(match.route.view());
};

// use router when browsing history
window.addEventListener("popstate", router);

document.addEventListener("DOMContentLoaded", () => {
  // navigate to paths with data link values aka push state method
  document.body.addEventListener("click", e => {
    if (e.target.matches("[data-link]")) {
      e.preventDefault();
      navigateTo(e.target.href);
    }
  });

  router();
});