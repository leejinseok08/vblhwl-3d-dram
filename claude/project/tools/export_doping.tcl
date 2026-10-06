# export_doping.tcl — dump the net doping of a 2D mesh on vertical cut lines (input of plot_struct.py).
#   EXP_TDR=<mesh.tdr> EXP_OUT=<dir> EXP_X0=0 EXP_X1=0.0746 EXP_NX=150 svisual -b export_doping.tcl
set d [load_file $env(EXP_TDR)]
set p [create_plot -dataset $d]
set nx $env(EXP_NX)
set var DopingConcentration
if {[info exists env(EXP_VAR)]} { set var $env(EXP_VAR) }      ;# any other field of a device plot
for {set i 0} {$i < $nx} {incr i} {
  set x [expr {$env(EXP_X0) + ($i + 0.5) * ($env(EXP_X1) - $env(EXP_X0)) / $nx}]
  if {[catch {
    set c [create_cutline -plot $p -type x -at $x]
    export_variables [list Y $var] -dataset $c -filename [format "%s/cut_%04d_%.6f.csv" $env(EXP_OUT) $i $x] -overwrite
  } err]} { puts "SKIP $i $x: $err" }
}
puts "DONE $nx"
exit
