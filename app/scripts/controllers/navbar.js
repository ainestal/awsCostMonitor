'use strict';

angular.module('awsCostMonitorApp')
  .controller('NavbarCtrl', function ($scope, $location) {
    $scope.menu = [{
      'title': 'Home',
      'link': '/'
    }
    // , {
    //   'title': 'Help',
    //   'link': '/help'
    // }, {
    //   'title': 'Settings',
    //   'link': '/settings'
    // }
    ];
    
    $scope.isActive = function(route) {
      return route === $location.path();
    };
  });
