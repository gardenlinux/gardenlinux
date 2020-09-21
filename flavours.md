flavour_sets:
  - name: 'all'


    flavour_combinations:

architecture x platfoms x modifiers  --- fails



      - architectures: [ 'amd64' ]
        platforms: [ metal ]
        modifiers: [ [ gardener, _prod ] , [ chost, _prod ] , [ vhost, _prod ] ]
        fails: [ unit, integration ]
