import _init_paths
import matplotlib
#matplotlib.use('pdf')
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from fast_rcnn.config import cfg
from fast_rcnn.test import im_detect
from fast_rcnn.nms_wrapper import nms
from utils.timer import Timer
import numpy as np
import os, sys, cv2
import argparse
from networks.factory import get_network

CLASSES =  ('__background__', # always index 0
                            '1_1', '1_2', '1_3', '2_2', '2_3', '3_3')

def vis_detections(im, class_name, dets,ax, thresh=0.5):
    """Draw detected bounding boxes."""
    inds = np.where(dets[:, -1] >= thresh)[0]
    if len(inds) == 0:
        # get a box with a highest score
        try:
            max_score = np.max(dets[:, -1])
            inds = np.where(dets[:, -1] == max_score)[0][0:1]
        except Exception as exp:
            print('inds == 0, but %s' % str(exp))
            return

    for i in inds:
        bbox = dets[i, :4]
        score = dets[i, -1]

        ax.add_patch(
            plt.Rectangle((bbox[0], bbox[1]),
                          bbox[2] - bbox[0],
                          bbox[3] - bbox[1], fill=False,
                          edgecolor=plt.cm.rainbow(i), linewidth=2.5)
            )
        #cns = class_name.split('_')
        #class_name = '%sC%sP' % (cns[0], cns[1])
        ax.text(bbox[0], bbox[1] - 2,
                '{:s} {:.3f}'.format(class_name, score),
                bbox=dict(facecolor='blue', alpha=0.5),
                fontsize=14, color='white')

    ax.set_title(('{} detections with '
                  'p({} | box) >= {:.1f}').format(class_name, class_name,
                                                  thresh),
                  fontsize=14)
    plt.axis('off')
    plt.tight_layout()
    plt.draw()


def demo(sess, net, image_name, input_path, conf_thresh=0.8):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    # im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im_file = os.path.join(input_path, image_name)
    #im_file = os.path.join('/home/corgi/Lab/label/pos_frame/ACCV/training/000001/',image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print ('Detection took {:.3f}s for '
           '{:d} object proposals').format(timer.total_time, boxes.shape[0])

    # Visualize detections for each class
    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(im, aspect='equal')

    #CONF_THRESH = 0.3
    NMS_THRESH = cfg.TEST.NMS #cfg.TEST.RPN_NMS_THRESH # 0.3
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        vis_detections(im, cls, dets, ax, thresh=conf_thresh)

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Faster R-CNN demo')
    parser.add_argument('--gpu', dest='gpu_id', help='GPU device id to use [0]',
                        default=0, type=int)
    parser.add_argument('--cpu', dest='cpu_mode',
                        help='Use CPU mode (overrides --gpu)',
                        action='store_true')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16]',
                        default='VGGnet_test14')
    parser.add_argument('--model', dest='model', help='Model path',
                        default='/group/pawsey0129/cwu/rgz-faster-rcnn/output/faster_rcnn_end2end/rgz_2017_train/VGGnet_fast_rcnn-50000')
    parser.add_argument('--input', dest='input_path', help='Input PNG path',
                        default='/home/cwu/rgz-faster-rcnn/data/RGZdevkit2017/RGZ2017/PNGImages')
    parser.add_argument('--figure', dest='fig_path', help='Figure path',
                        default='/group/pawsey0129/cwu/output')
    parser.add_argument('--threshold', dest='conf_thresh', help='confidence threshold',
                        default=0.8, type=float)

    args = parser.parse_args()

    return args
if __name__ == '__main__':
    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    cfg.TEST.RPN_MIN_SIZE = 4
    cfg.TEST.RPN_POST_NMS_TOP_N = 4

    args = parse_args()

    if args.model == ' ':
        raise IOError(('Error: Model not found.\n'))

    # init session
    sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    # load network
    net = get_network(args.demo_net)
    # load model
    saver = tf.train.Saver(write_version=tf.train.SaverDef.V1)
    saver.restore(sess, args.model)

    #sess.run(tf.initialize_all_variables())

    print '\n\nLoaded network {:s}'.format(args.model)

    # Warmup on a dummy image
    im = 128 * np.ones((300, 300, 3), dtype=np.uint8)
    for i in xrange(2):
        _, _= im_detect(sess, net, im)

    im_names = ['FIRSTJ094204.6+480448_radio.png',  'FIRSTJ122547.1+594111_radio.png',  'FIRSTJ145825.3+484239_radio.png',  'FIRSTJ233909.5+113426_radio.png',
'FIRSTJ094206.5+544626_radio.png',  'FIRSTJ122547.8+051905_radio.png',  'FIRSTJ145826.0+522419_radio.png',  'FIRSTJ233912.1+105429_radio.png',
'FIRSTJ094207.6+433848_radio.png',  'FIRSTJ122549.6+163347_radio.png',  'FIRSTJ145834.8+215228_radio.png',  'FIRSTJ233921.6+064203_radio.png',
'FIRSTJ094213.8+124534_radio.png',  'FIRSTJ122552.1+634005_radio.png',  'FIRSTJ145852.0+433709_radio.png',  'FIRSTJ233939.4+020030_radio.png',
'FIRSTJ094215.3+062820_radio.png',  'FIRSTJ122555.1+153436_radio.png',  'FIRSTJ145858.8+260859_radio.png',  'FIRSTJ233954.0+115948_radio.png',
'FIRSTJ094220.3+163949_radio.png',  'FIRSTJ122600.9+084106_radio.png',  'FIRSTJ145901.3+271124_radio.png',  'FIRSTJ234004.0+021817_radio.png',
'FIRSTJ094224.1+222307_radio.png',  'FIRSTJ122608.8+473711_radio.png',  'FIRSTJ145901.5+231026_radio.png',  'FIRSTJ234235.1+103235_radio.png',
'FIRSTJ094226.6+340231_radio.png',  'FIRSTJ122609.5+584421_radio.png',  'FIRSTJ145905.9+392409_radio.png',  'FIRSTJ234247.4+142649_radio.png',
'FIRSTJ094228.0+340243_radio.png',  'FIRSTJ122612.8+062727_radio.png',  'FIRSTJ145908.0+381509_radio.png',  'FIRSTJ234253.1+094248_radio.png']

    for i, im_name in enumerate(im_names):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Demo for data/demo/{}'.format(im_name)
        demo(sess, net, im_name, args.input_path, conf_thresh=args.conf_thresh)
        plt.savefig(os.path.join(args.fig_path, im_name.replace('.png', '_pred.png')))
        try:
            plt.close()
        except:
            pass
