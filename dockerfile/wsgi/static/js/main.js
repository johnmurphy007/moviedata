'use strict';   // See note about 'use strict'

var app = angular.module('app', []);

// app.config(['$routeProvider', function($routeProvider) {
//   $routeProvider
//     .when('movieinfo/all', {
//       templateUrl: '/movieinfoall.html',
//       controller: 'Moviedisplaycontroller'
//     })
//     .otherwise({ redirectTo: '/movieinfo'});
// }])
// .factory('windowAlert', [
//   '$window',
//   function($window) {
//     return $window.alert;
//   }
// ]);

// app.config(['$interpolateProvider', function($interpolateProvider) {
//   $interpolateProvider.startSymbol('{[');
//   $interpolateProvider.endSymbol(']}');
// }]);

app.controller('Moviedisplaycontroller', ['$scope', '$http', function($scope, $http) {

   $scope.showDetails = false;
   $scope.result = 5;

   $scope.toggleDetails = function() {
   $scope.showDetails = !$scope.showDetails;
  };

}]);
