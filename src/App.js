import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import Viz from "./Viz";

class App extends Component {

    state = {
        searchQueryString: ""
    }

    constructor(props) {
        super(props)
        this.svgSize = {
            availableSpace: {
                width: 700,
                height: 300,
            },
            margin: {
                top: 50,
                left: 80,
                right: 50,
                bottom: 80,
            }
        }
    }

    render() {
        return (
            <div className="App">
                <header className="App-header">
                    <h1>
                        Vizsualizing Fortune 1000's Glassdoor Rating
                    </h1>
                </header>
                <Viz
                    svgSize={this.svgSize}
                />
            </div>
        );
    }
}

export default App;
