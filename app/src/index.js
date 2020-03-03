import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import { Route, BrowserRouter as Router } from 'react-router-dom';

import Home from './components/Home/Home';
import * as serviceWorker from './serviceWorker';

const routing = (
  <Router>
    <div className="router">
      <div className="router-menu" id="router-menu">
        <h5 className="router-menu-header">Yogi Love</h5>
      </div>
      <div className="router-view">
        <Route exact path="/" component={Home} />
      </div>
    </div>
  </Router>
);

ReactDOM.render(routing, document.getElementById('root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
