import React, { Component } from 'react'
import PropTypes from 'prop-types'

import * as d3 from "d3";
import "d3-selection-multi";

import jsonData from "./data/sample-company-ratings.json";
import "./Viz.scss"

export default class Viz extends Component {

    xScale;
    yScale;
    svg;
    transitionDuration = 300;

    static propTypes = {
        // prop: PropTypes
        svgSize: PropTypes.shape({
            availableSpace: PropTypes.shape({
                width: PropTypes.number,
                height: PropTypes.number,
            }),
            margin: PropTypes.shape({
                top: PropTypes.number,
                left: PropTypes.number,
                right: PropTypes.number,
                bottom: PropTypes.number,
            })
        })
    }

    constructor(props) {
        super(props)
    }

    componentDidMount() {
        this.setState({
            data: this.cleanData(jsonData.items)
        })
    }

    componentDidUpdate() {
        this.transition = d3.transition().duration(this.transitionDuration);

        this.initializeScale()
        this.initializeVizSpace()

        this.initializeAxis()
        this.updateDots()
    }

    /**
     * Data Processing
     */

    cleanData(data = []) {
        return data.filter((d) => {
            return (
                d.glassdoorRating !== undefined
            )
        })
    }

    /**
     * Helper Functions
     */

    getSvgOuterWidth() {
        return (
            this.props.svgSize.availableSpace.width +
            this.props.svgSize.margin.left +
            this.props.svgSize.margin.right
        )
    }

    getSvgOuterHeight() {
        return (
            this.props.svgSize.availableSpace.height +
            this.props.svgSize.margin.top +
            this.props.svgSize.margin.bottom
        )
    }

    /**
     * D3 Function
     */

    initializeVizSpace() {
        // initialize svg
        this.svg = d3.select(this.node)
            .attrs({
                viewBox: `0 0 ${this.getSvgOuterWidth()} ${this.getSvgOuterHeight()}`,
                preserveAspectRatio: `xMidYMid meet`
            })
        ;
        
        //make a clip path to prevent zooming from overflow
        let width = this.props.svgSize.availableSpace.width;
        let height = this.props.svgSize.availableSpace.height;
        this.svg.append("defs").append("svg:clipPath")
            .attr("id", "clip")
            .append("svg:rect")
            .attr("id", "clip-rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("height", height)
            .attr("width", width);
        this.svg = this.svg.append("g")
            .attrs({
                "transform": `translate(${this.props.svgSize.margin.left}, ${this.props.svgSize.margin.top})`,
                // "clip-path": "url(#clip)"
            })
        ;
        
        // initialize zoom
        this.zoom = d3.zoom()
            .scaleExtent([1, 5])
            .on("zoom", this.zoomHandler)

        // initialize zoom area (non-transparent)
        this.zoomArea = this.svg.append('rect')
            .attrs({
                // x: this.props.svgSize.margin.left,
                // y: this.props.svgSize.margin.top,
                class: `zoom-area`,
                width: this.props.svgSize.availableSpace.width,
                height: this.props.svgSize.availableSpace.height,

            })
            .call(this.zoom)
        ;
        this.svg.call(this.zoom);
        

        // intialize tooltip
        this.tooltipBox = d3.select('body').append('div')
            .attrs({
                class: `tooltip-box`
            })
            .styles({
                opacity: 0
            })
    }

    zoomHandler = () => {
        var zoomedXScale = d3.event.transform.rescaleX(this.xScale)
        var zoomedYScale = d3.event.transform.rescaleY(this.yScale)

        // update axes
        this.xAxis.call(d3.axisBottom(this.xScale).scale(zoomedXScale));
        this.yAxis.call(d3.axisLeft(this.yScale).scale(zoomedYScale));

        // update dots
        this.dots.attrs({
            "transform": d3.event.transform,
            // "r": `${4 / d3.event.transform.k}px`
        })
    }

    initializeScale() {
        this.xScale = d3.scaleLinear()
            .domain([0, d3.max(this.state.data.map((d) => d.fortune500Rank))])
            .range([0, this.props.svgSize.availableSpace.width])
            ;

        this.yScale = d3.scaleLinear()
            .domain([0, d3.max(this.state.data.map((d) => {
                return d.glassdoorRating
            }))])
            .range([this.props.svgSize.availableSpace.height, 0])
            ;
    }

    initializeAxis() {
        this.xAxis = this.svg.append("g")
            .attrs({
                class: 'x-axis',
                transform: `translate(0, ${this.props.svgSize.availableSpace.height})`
            })
            .call(d3.axisBottom(this.xScale))

        this.yAxis = this.svg.append("g")
            .attrs({
                "class": "y-axis"
            })
            .call(d3.axisLeft(this.yScale))

        // text label for the x axis
        this.svg.append("text")
            .attr("transform",
                "translate(" + (this.props.svgSize.availableSpace.width / 2) + " ," +
                (this.props.svgSize.availableSpace.height + this.props.svgSize.margin.top) + ")")
            .style("text-anchor", "middle")
            .text("Fortune Ranking");

        // text label for the y axis
        this.svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - this.props.svgSize.margin.left * 0.8)
            .attr("x", 0 - (this.props.svgSize.availableSpace.height / 2))
            .attr("dy", "1em")
            .style("text-anchor", "middle")
            .text("Glassdoor Rating")
    }

    updateDots() {
        this.dots = this.svg.selectAll(".dot").data(this.state.data, (d) => {
            return d.companyTitle;
        })

        // new 
        this.dots = this.dots.enter().append("circle")
            .attrs({
                class: `dot`,
                r: 1.3,
                cx: (d) => this.xScale(d.fortune500Rank),
                cy: (d) => this.yScale(d.glassdoorRating),
                fill: "red",
            })
            .on("mousemove", (d) => {
                this.tooltipBox
                    .styles({
                        left: `${d3.event.pageX - 100}px`,
                        top: `${d3.event.pageY + 45}px`,
                        opacity: 0.9
                    })
                    .html(`
                        <span><strong>Company</strong>: ${d.companyTitle}</span>
                        <span><strong>GD Rating</strong>: ${d.glassdoorRating}</span>
                        <span><strong>Fortune Rank</strong>: ${d.fortune500Rank}</span>
                    `)
                    ;
            })
            .on("mouseout", (d) => {
                this.tooltipBox
                    .styles({
                        opacity: 0
                    })
                    ;
            })
        // udpate

        // remove
    }

    render() {
        return (
            <div className="svg-container">
                <svg className="svg-content" ref={node => this.node = node}
                >
                </svg>
            </div>
        )
    }
}
