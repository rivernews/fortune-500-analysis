# fortune-500-analysis

Data sampled on Nov 14, 2018. [See Demo Page Here.](https://rivernews.github.io/fortune-500-analysis/)

## TODO

- [x] Have to handle case when there's only one result, gd page will be different.
- [ ] We also need review # for reliability 
- [ ] Have to handle company names have spaces when querying
- [ ] Handle overflow problem - [clipping](https://stackoverflow.com/questions/34130019/d3-js-zoom-without-overflow) is still not a good choice since axis will not show. [This guy](https://medium.com/@xoor/implementing-charts-that-scale-with-d3-and-canvas-part-2-d9f657f2757b) somehow did what we want.
- [x] Making [d3 chart responsive](https://chartio.com/resources/tutorials/how-to-resize-an-svg-when-the-window-is-resized-in-d3-js/)
- [x] Deploy to github by `npm run deploy`
- ~~Scroll down to load more of the list~~
- [x] [Scatter Plot](https://bl.ocks.org/sebg/6f7f1dd55e0c52ce5ee0dac2b2769f4b)
- [x] Zoom
  - [Easy zoom example](https://bl.ocks.org/rutgerhofste/5bd5b06f7817f0ff3ba1daa64dee629d)

## Dependencies (Frontend React)

- Create react app
- `npm i d3 gh-pages d3-selection-multi node-sass`
- Setup d3 dom / node

## Dependencies (Backend Data)

- [requests](http://docs.python-requests.org/en/master/)
- [Selenium Walkthrough](https://medium.com/the-andela-way/introduction-to-web-scraping-using-selenium-7ec377a8cf72)
  - [Selenium Setup](https://medium.com/@bach_illusions/python-and-selenium-cf451141716)
  - [Offocial](https://selenium-python.readthedocs.io/installation.html)
