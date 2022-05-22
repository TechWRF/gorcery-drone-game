import AbstractView from "./AbstractView.js";

export default class extends AbstractView {
  constructor() {
    super();
    this.setTitle("GameView");
  }
//https://www.anychart.com/blog/2021/07/28/line-chart-js/
  async getHtml() {
    return `
    `;
  }
}