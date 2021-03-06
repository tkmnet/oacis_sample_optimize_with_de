import sys
import oacis
from de_optimizer import DE_Optimizer

if len(sys.argv) != 6:
    print("Usage: oacis_python optimize_with_oacis.py <num_iterations> <population size> <f> <cr> <seed>")
    raise RuntimeError("invalid number of arguments")

num_iter = int(sys.argv[1])
n = int(sys.argv[2])
f = float(sys.argv[3])
cr = float(sys.argv[4])
seed = int(sys.argv[5])
opt_param = {"num_iter": num_iter, "n": n, "f": f, "cr": cr, "seed": seed}
#print("given parameters : num_iter %d, n: %d, f: %f, cr: %f, seed: %d" % (num_iter,n,f,cr,seed))
print("given parameters : %s" % repr(opt_param) )

def optimize_p1p2( p3, opt_param ):
    sim = oacis.Simulator.find_by_name("de_optimize_test2")
    host = oacis.Host.find_by_name("localhost")
    domains = [
        {'min': -10.0, 'max': 10.0},
        {'min': -10.0, 'max': 10.0}
    ]

    def map_agents(agents):
        parameter_sets = []
        for x in agents:
            ps = sim.find_or_create_parameter_set( {'p1':x[0], 'p2':x[1], 'p3':p3} )
            runs = ps.find_or_create_runs_upto(1, submitted_to=host)
            print("Created a new PS: %s" % str(ps.id()) )
            parameter_sets.append(ps)
        oacis.OacisWatcher.await_all_ps(parameter_sets) # Wait until all parameter_sets complete
        results = [ps.runs().first().result()['f'] for ps in parameter_sets]
        return results

    opt = DE_Optimizer(map_agents, domains,
            n=opt_param['n'], f=opt_param['f'], cr=opt_param['cr'],
            rand_seed=opt_param['seed'])

    for t in range(opt_param['num_iter']):
        opt.proceed()
        print("t=%d  %s, %f, %f" % (t, repr(opt.best_point), opt.best_f, opt.average_f() ) )

w = oacis.OacisWatcher()
p3_list = [0.0,1.0,2.0]
for p3 in p3_list:
    w.async( lambda: optimize_p1p2(p3,opt_param) )
w.loop()

