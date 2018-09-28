import os
import thread
import threading

from jsonschema import validate, ValidationError
from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest
from faiss_index import FaissIndex
import uwsgidecorators

try:
    import uwsgi
except ImportError:
    print('Failed to load python module uwsgi')
    print('Periodic faiss index updates isn\'t enabled')

    uwsgi = None

blueprint = Blueprint('faiss_index', __name__)
cur = [1]
faiss_index_list = [None, None]
monitor_file = '/Users/yahui.yan/SourceTree/faiss-web-service/faiss_index_files/index.timestamp'
last_timestamp = ['']


@blueprint.record_once
def record(setup_state):

    # manage_faiss_index(
    #     setup_state.app.config.get('GET_FAISS_RESOURCES'),
    #     setup_state.app.config['GET_FAISS_INDEX'],
    #     setup_state.app.config['GET_FAISS_ID_TO_VECTOR'],
    #     setup_state.app.config.get('UPDATE_FAISS_AFTER_SECONDS'))

    init_faiss_index(setup_state.app.config.get('GET_FAISS_INDEX'),
                     setup_state.app.config['GET_FAISS_ID_TO_VECTOR'],
                     cur,
                     faiss_index_list,
                     monitor_file)

    # sec_init_faiss_index(setup_state.app.config.get('GET_FAISS_INDEX'),
    #                  setup_state.app.config['GET_FAISS_ID_TO_VECTOR'],
    #                  cur,
    #                  faiss_index_list,
    #                  monitor_file)


@blueprint.route('/faiss/search', methods=['POST'])
def search():
    try:
        json = request.get_json(force=True)
        print json
        validate(json, {
            'type': 'object',
            'required': ['k'],
            'properties': {
                'k': {'type': 'integer', 'minimum': 1},
                'ids': {'type': 'array', 'items': {'type': 'number'}},
                'vectors': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {'type': 'number'}
                    }
                }
            }
        })
        print "\n\n=========================================================="
        print 'cur:', cur[0]
        faiss_index = faiss_index_list[cur[0]]
        print 'current faiss_index:', faiss_index
        print 'current pid:', os.getpid()
        print "==========================================================\n\n"

        results_ids = faiss_index.search_by_ids(json['ids'], json['k']) if 'ids' in json else []
        results_vectors = faiss_index.search_by_vectors(json['vectors'], json['k']) if 'vectors' in json else []

        return jsonify(results_ids + results_vectors)

    except (BadRequest, ValidationError) as e:
        print('Bad request', e)
        return 'Bad request', 400

    except Exception as e:
        print('Server error', e)
        print e.message
        return 'Server error', 500


def update_index(get_faiss_index, get_faiss_id_to_vector, cur, faiss_index_list):
    file_name = str(os.getpid()) + '.log'
    f = open(file_name, 'a')
    print "\n\n========================================================================"
    f.write("\n\n========================================================================\n")
    f.write('Getting Faiss index of [%s]\n' % cur[0])
    # print "set pid -> %s" % os.getpid()
    print('Getting Faiss index of [%s]' % cur[0])

    faiss_index_list[1 - cur[0]] = FaissIndex(get_faiss_index(), get_faiss_id_to_vector())
    print 'faiss_index_0:', faiss_index_list[0]
    print 'faiss_index_1:', faiss_index_list[1]
    print('Getting Faiss index done')

    f.write('faiss_index_0:{}\n'.format(faiss_index_list[0]))
    f.write('faiss_index_1:{}\n'.format(faiss_index_list[1]))
    f.write('Getting Faiss index done\n')

    cur[0] = 1 - cur[0]
    print('cur from %s -> %s' % (1 - cur[0], cur[0]))
    print 'current pid:', os.getpid()
    print "========================================================================\n\n"

    f.write('cur from %s -> %s\n' % (1 - cur[0], cur[0]))
    f.write('current pid:%s\n' % os.getpid())
    f.write("========================================================================\n\n")


def init_faiss_index(get_faiss_index, get_faiss_id_to_vector, cur, faiss_index_list, file_path):
    reload_faiss_index_signum = 3

    @uwsgidecorators.filemon(file_path, signum=reload_faiss_index_signum, target='workers')
    def reload_faiss_index(signal=None):
        threading.Thread(target=update_index, args=(get_faiss_index, get_faiss_id_to_vector, cur, faiss_index_list)).run()
        # update_index(get_faiss_index, get_faiss_id_to_vector, cur, faiss_index_list)

    update_index(get_faiss_index, get_faiss_id_to_vector, cur, faiss_index_list)
