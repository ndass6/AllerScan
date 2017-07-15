import React from 'react';
import {Router, Route, IndexRoute, hashHistory} from 'react-router';
import {Main, Home} from '../components/Components';
import {ViewContainer} from '../containers/ViewContainer'

var routes = (
  <Router history={hashHistory}>
    <Route path='/' component={Main}>
      <IndexRoute component={Home} />
      <Route path='view' component={ViewContainer} />
    </Route>
  </Router>
);

module.exports = routes;
