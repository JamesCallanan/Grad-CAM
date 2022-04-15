
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def make_gradcam_heatmap(img_array, model, last_conv_layer_name, pred_index=None):
    # Check image dimensions are okay - image dimensions must match form that network will accept + batch size must equal 1
    if img_array.shape[0] > 1:
      return 'Error with make_gradcam_heatmap()!\nBatch size for img_array parameter is greater than 1.\nGrad-CAM can only be applied to individual images.\nThis fn would pool gradients over multiple images and give incorrect results.'
    
    # Remove last layer's softmax
    model.layers[-1].activation = None    

    grad_model = tf.keras.models.Model(
        [model.inputs], [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        last_conv_layer_output, preds = grad_model(img_array)
        if pred_index is None:
            pred_index = tf.argmax(preds[0])
        class_channel = preds[:, pred_index]

    grads = tape.gradient(class_channel, last_conv_layer_output)
    last_conv_layer_output = last_conv_layer_output[0]

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    
    grad_cam_heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis] #@operator will do a matrix multiplication and 512 feature map axis will dissapear
    grad_cam_heatmap = tf.squeeze(grad_cam_heatmap)
    grad_cam_heatmap = tf.maximum(grad_cam_heatmap, 0) / tf.math.reduce_max(grad_cam_heatmap)
    
    #HiResCAM
    hi_res_cam_heatmap = tf.math.multiply(last_conv_layer_output,grads[0])
    hi_res_cam_heatmap = tf.reduce_mean(hi_res_cam_heatmap,-1) #Needed to average over different feature map layers
    hi_res_cam_heatmap = tf.maximum(hi_res_cam_heatmap, 0) / tf.math.reduce_max(hi_res_cam_heatmap)

    return grad_cam_heatmap.numpy(), hi_res_cam_heatmap.numpy()

def display_gradcam_heatmap(mri, heatmap, alpha=0.5, beta=0.5):
    if len(mri.shape) != 3:
      return 'Incorrect length mri'
    mri = (255*(mri/np.amax(mri)))
    # Rescale heatmap to a range 0-255
    heatmap = np.uint8(255 * heatmap)

    # Should consider another colour map according to Kathleen?
    jet = cm.get_cmap("jet")

    # Use RGB values of the colormap
    jet_colors = jet(np.arange(256))[:, :3]
    jet_heatmap = jet_colors[heatmap]

    # Create an image with RGB colorized heatmap
    jet_heatmap = tf.keras.preprocessing.image.array_to_img(jet_heatmap)

    jet_heatmap = jet_heatmap.resize((mri.shape[1], mri.shape[0]))
    jet_heatmap = tf.keras.preprocessing.image.img_to_array(jet_heatmap)

    # Superimpose the heatmap on original image
    superimposed_img = jet_heatmap*alpha +  mri*beta
    superimposed_img = superimposed_img.astype(int)
    plt.imshow(superimposed_img)