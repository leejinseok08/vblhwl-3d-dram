# export_map.tcl - dump fields of a 2D device plot on vertical cut lines (one CSV per cut; gt_map.sh joins them).
#   MAP_TDR=<file.tdr> MAP_OUT=<dir> MAP_X0=<um> MAP_X1=<um> MAP_NX=<n> MAP_VARS="Abs(ElectricField-V) Band2BandGeneration" svisual -b export_map.tcl
# MAP_VARS empty: only list the fields of the file.
set d [load_file $env(MAP_TDR)]
set p [create_plot -dataset $d]
puts "FIELDS: [list_fields -plot $p]"
if {![info exists env(MAP_VARS)] || $env(MAP_VARS) eq ""} { exit }
set nx $env(MAP_NX)
for {set i 0} {$i < $nx} {incr i} {
  set x [expr {$env(MAP_X0) + ($i + 0.5) * ($env(MAP_X1) - $env(MAP_X0)) / $nx}]
  if {[catch {
    set c [create_cutline -plot $p -type x -at $x]
    export_variables [concat Y $env(MAP_VARS)] -dataset $c -filename [format "%s/cut_%04d_%.6f.csv" $env(MAP_OUT) $i $x] -overwrite
  } err]} { puts "SKIP $i $x: $err" }
}
puts "DONE $nx"
exit
