# chk_struct.tcl — list regions/contacts of a mesh and dump net doping along a vertical cut.
# Called by build_check.sh:  CHK_TDR=<mesh.tdr> CHK_X=<x in um> CHK_OUT=<csv> svisual -b chk_struct.tcl
set d [load_file $env(CHK_TDR)]
set p [create_plot -dataset $d]
puts "REGIONS: [list_regions -plot $p]"
set c [create_cutline -plot $p -type x -at $env(CHK_X)]
export_variables {Y DopingConcentration} -dataset $c -filename $env(CHK_OUT) -overwrite
# horizontal cut at body mid-height (y = 0.090 um for the default geometry)
set h [create_cutline -plot $p -type y -at $env(CHK_Y)]
export_variables {X DopingConcentration} -dataset $h -filename $env(CHK_OUTH) -overwrite
exit
