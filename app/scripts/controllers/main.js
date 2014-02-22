'use strict';

angular.module('awsCostMonitorApp')
  .filter('reverse', function() {
    return function(items) {
      return items.slice().reverse();
    };
  });

angular.module('awsCostMonitorApp')
  .controller('MainCtrl', function ($scope, $http) {

    $scope.awesomeThings = [
      'HTML5 Boilerplate',
      'AngularJS',
      'Karma'
    ];
    $scope.totalCost = 0;
    $scope.oneAtATime = true;

    $http.get('/api/all')
      .success(function(response) {
        $scope.instancesList = response[0];
        $scope.volumesList   = response[1];
        $scope.totalCost      = 0;

// solo está insertando en la primera instancia
        for (var i = 0; i < $scope.instancesList.length; i++){
          $scope.instancesList[i]['volumes'] = [];
          for (var j = 0; j < $scope.volumesList.length; j++){
            if ($scope.instancesList[i]['id'] == $scope.volumesList[j]['instance_id']){              
              $scope.instancesList[i]['volumes'].push($scope.volumesList[j]);
            }
          }
          if ($scope.instancesList[i]['current_cost'] != 'N/A. Stopped instance'){
            $scope.totalCost = $scope.totalCost + $scope.instancesList[i]['current_cost'];
          }
        };
      })
      .error(console.log('error retrieving the list'));
  });
