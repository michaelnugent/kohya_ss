# v1: initial release
# v2: add open and save folder icons
# v3: Add new Utilities tab for Dreambooth folder preparation
# v3.1: Adding captionning of images to utilities

import gradio as gr
import logging
import time

# import easygui
import json
import math
import os
import subprocess
import pathlib
import argparse
from library.common_gui import (
    get_folder_path,
    remove_doublequote,
    get_file_path,
    get_any_file_path,
    get_saveasfile_path,
    color_aug_changed,
    save_inference_file,
    gradio_advanced_training,
    run_cmd_advanced_training,
    gradio_training,
    gradio_config,
    gradio_source_model,
    run_cmd_training,
    # set_legacy_8bitadam,
    update_my_data,
    check_if_model_exist,
    output_message,
)
from library.dreambooth_folder_creation_gui import (
    gradio_dreambooth_folder_creation_tab,
)
from library.tensorboard_gui import (
    gradio_tensorboard,
    start_tensorboard,
    stop_tensorboard,
)
from library.dataset_balancing_gui import gradio_dataset_balancing_tab
from library.utilities import utilities_tab
from library.merge_lora_gui import gradio_merge_lora_tab
from library.svd_merge_lora_gui import gradio_svd_merge_lora_tab
from library.verify_lora_gui import gradio_verify_lora_tab
from library.resize_lora_gui import gradio_resize_lora_tab
from library.sampler_gui import sample_gradio_config, run_cmd_sample

from library.custom_logging import setup_logging

# Set up logging
log = setup_logging()

# from easygui import msgbox

folder_symbol = '\U0001f4c2'  # 📂
refresh_symbol = '\U0001f504'  # 🔄
save_style_symbol = '\U0001f4be'  # 💾
document_symbol = '\U0001F4C4'   # 📄
path_of_this_folder = os.getcwd()


def save_configuration(
    save_as,
    file_path,
    pretrained_model_name_or_path,
    v2,
    v_parameterization,
    logging_dir,
    train_data_dir,
    reg_data_dir,
    output_dir,
    max_resolution,
    learning_rate,
    lr_scheduler,
    lr_warmup,
    train_batch_size,
    epoch,
    save_every_n_epochs,
    mixed_precision,
    save_precision,
    seed,
    num_cpu_threads_per_process,
    cache_latents,
    cache_latents_to_disk,
    caption_extension,
    enable_bucket,
    gradient_checkpointing,
    full_fp16,
    no_token_padding,
    stop_text_encoder_training,
    # use_8bit_adam,
    xformers,
    save_model_as,
    shuffle_caption,
    save_state,
    resume,
    prior_loss_weight,
    text_encoder_lr,
    unet_lr,
    network_dim,
    lora_network_weights,
    dim_from_weights,
    color_aug,
    flip_aug,
    clip_skip,
    gradient_accumulation_steps,
    mem_eff_attn,
    output_name,
    model_list,
    max_token_length,
    max_train_epochs,
    max_data_loader_n_workers,
    network_alpha,
    training_comment,
    keep_tokens,
    lr_scheduler_num_cycles,
    lr_scheduler_power,
    persistent_data_loader_workers,
    bucket_no_upscale,
    random_crop,
    bucket_reso_steps,
    caption_dropout_every_n_epochs,
    caption_dropout_rate,
    optimizer,
    optimizer_args,
    noise_offset_type,
    noise_offset,
    adaptive_noise_scale,
    multires_noise_iterations,
    multires_noise_discount,
    LoRA_type,
    conv_dim,
    conv_alpha,
    sample_every_n_steps,
    sample_every_n_epochs,
    sample_sampler,
    sample_prompts,
    additional_parameters,
    vae_batch_size,
    min_snr_gamma,
    down_lr_weight,
    mid_lr_weight,
    up_lr_weight,
    block_lr_zero_threshold,
    block_dims,
    block_alphas,
    conv_dims,
    conv_alphas,
    weighted_captions,
    unit,
    save_every_n_steps,
    save_last_n_steps,
    save_last_n_steps_state,
    use_wandb,
    wandb_api_key,
    scale_v_pred_loss_like_noise_pred,
    scale_weight_norms,
    network_dropout,
    rank_dropout,
    module_dropout,
):
    # Get list of function parameters and values
    parameters = list(locals().items())

    original_file_path = file_path

    save_as_bool = True if save_as.get('label') == 'True' else False

    if save_as_bool:
        log.info('Save as...')
        file_path = get_saveasfile_path(file_path)
    else:
        log.info('Save...')
        if file_path == None or file_path == '':
            file_path = get_saveasfile_path(file_path)

    # log.info(file_path)

    if file_path == None or file_path == '':
        return original_file_path  # In case a file_path was provided and the user decide to cancel the open action

    # Return the values of the variables as a dictionary
    variables = {
        name: value
        for name, value in parameters  # locals().items()
        if name
        not in [
            'file_path',
            'save_as',
        ]
    }

    # Extract the destination directory from the file path
    destination_directory = os.path.dirname(file_path)

    # Create the destination directory if it doesn't exist
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    # Save the data to the selected file
    with open(file_path, 'w') as file:
        json.dump(variables, file, indent=2)

    return file_path


def open_configuration(
    ask_for_file,
    file_path,
    pretrained_model_name_or_path,
    v2,
    v_parameterization,
    logging_dir,
    train_data_dir,
    reg_data_dir,
    output_dir,
    max_resolution,
    learning_rate,
    lr_scheduler,
    lr_warmup,
    train_batch_size,
    epoch,
    save_every_n_epochs,
    mixed_precision,
    save_precision,
    seed,
    num_cpu_threads_per_process,
    cache_latents,
    cache_latents_to_disk,
    caption_extension,
    enable_bucket,
    gradient_checkpointing,
    full_fp16,
    no_token_padding,
    stop_text_encoder_training,
    # use_8bit_adam,
    xformers,
    save_model_as,
    shuffle_caption,
    save_state,
    resume,
    prior_loss_weight,
    text_encoder_lr,
    unet_lr,
    network_dim,
    lora_network_weights,
    dim_from_weights,
    color_aug,
    flip_aug,
    clip_skip,
    gradient_accumulation_steps,
    mem_eff_attn,
    output_name,
    model_list,
    max_token_length,
    max_train_epochs,
    max_data_loader_n_workers,
    network_alpha,
    training_comment,
    keep_tokens,
    lr_scheduler_num_cycles,
    lr_scheduler_power,
    persistent_data_loader_workers,
    bucket_no_upscale,
    random_crop,
    bucket_reso_steps,
    caption_dropout_every_n_epochs,
    caption_dropout_rate,
    optimizer,
    optimizer_args,
    noise_offset_type,
    noise_offset,
    adaptive_noise_scale,
    multires_noise_iterations,
    multires_noise_discount,
    LoRA_type,
    conv_dim,
    conv_alpha,
    sample_every_n_steps,
    sample_every_n_epochs,
    sample_sampler,
    sample_prompts,
    additional_parameters,
    vae_batch_size,
    min_snr_gamma,
    down_lr_weight,
    mid_lr_weight,
    up_lr_weight,
    block_lr_zero_threshold,
    block_dims,
    block_alphas,
    conv_dims,
    conv_alphas,
    weighted_captions,
    unit,
    save_every_n_steps,
    save_last_n_steps,
    save_last_n_steps_state,
    use_wandb,
    wandb_api_key,
    scale_v_pred_loss_like_noise_pred,
    scale_weight_norms,
    network_dropout,
    rank_dropout,
    module_dropout,
):
    # Get list of function parameters and values
    parameters = list(locals().items())

    ask_for_file = True if ask_for_file.get('label') == 'True' else False

    original_file_path = file_path

    if ask_for_file:
        file_path = get_file_path(file_path)

    if not file_path == '' and not file_path == None:
        # load variables from JSON file
        with open(file_path, 'r') as f:
            my_data = json.load(f)
            log.info('Loading config...')

            # Update values to fix deprecated use_8bit_adam checkbox, set appropriate optimizer if it is set to True, etc.
            my_data = update_my_data(my_data)
    else:
        file_path = original_file_path  # In case a file_path was provided and the user decide to cancel the open action
        my_data = {}

    values = [file_path]
    for key, value in parameters:
        # Set the value in the dictionary to the corresponding value in `my_data`, or the default value if not found
        if not key in ['ask_for_file', 'file_path']:
            values.append(my_data.get(key, value))

    # This next section is about making the LoCon parameters visible if LoRA_type = 'Standard'
    if my_data.get('LoRA_type', 'Standard') == 'LoCon':
        values.append(gr.Row.update(visible=True))
    else:
        values.append(gr.Row.update(visible=False))

    return tuple(values)


def train_model(
    headless,
    print_only,
    pretrained_model_name_or_path,
    v2,
    v_parameterization,
    logging_dir,
    train_data_dir,
    reg_data_dir,
    output_dir,
    max_resolution,
    learning_rate,
    lr_scheduler,
    lr_warmup,
    train_batch_size,
    epoch,
    save_every_n_epochs,
    mixed_precision,
    save_precision,
    seed,
    num_cpu_threads_per_process,
    cache_latents,
    cache_latents_to_disk,
    caption_extension,
    enable_bucket,
    gradient_checkpointing,
    full_fp16,
    no_token_padding,
    stop_text_encoder_training_pct,
    # use_8bit_adam,
    xformers,
    save_model_as,
    shuffle_caption,
    save_state,
    resume,
    prior_loss_weight,
    text_encoder_lr,
    unet_lr,
    network_dim,
    lora_network_weights,
    dim_from_weights,
    color_aug,
    flip_aug,
    clip_skip,
    gradient_accumulation_steps,
    mem_eff_attn,
    output_name,
    model_list,  # Keep this. Yes, it is unused here but required given the common list used
    max_token_length,
    max_train_epochs,
    max_data_loader_n_workers,
    network_alpha,
    training_comment,
    keep_tokens,
    lr_scheduler_num_cycles,
    lr_scheduler_power,
    persistent_data_loader_workers,
    bucket_no_upscale,
    random_crop,
    bucket_reso_steps,
    caption_dropout_every_n_epochs,
    caption_dropout_rate,
    optimizer,
    optimizer_args,
    noise_offset_type,
    noise_offset,
    adaptive_noise_scale,
    multires_noise_iterations,
    multires_noise_discount,
    LoRA_type,
    conv_dim,
    conv_alpha,
    sample_every_n_steps,
    sample_every_n_epochs,
    sample_sampler,
    sample_prompts,
    additional_parameters,
    vae_batch_size,
    min_snr_gamma,
    down_lr_weight,
    mid_lr_weight,
    up_lr_weight,
    block_lr_zero_threshold,
    block_dims,
    block_alphas,
    conv_dims,
    conv_alphas,
    weighted_captions,
    unit,
    save_every_n_steps,
    save_last_n_steps,
    save_last_n_steps_state,
    use_wandb,
    wandb_api_key,
    scale_v_pred_loss_like_noise_pred,
    scale_weight_norms,
    network_dropout,
    rank_dropout,
    module_dropout,
):
    print_only_bool = True if print_only.get('label') == 'True' else False
    log.info(f'Start training LoRA {LoRA_type} ...')
    headless_bool = True if headless.get('label') == 'True' else False

    if pretrained_model_name_or_path == '':
        output_message(
            msg='Source model information is missing', headless=headless_bool
        )
        return

    if train_data_dir == '':
        output_message(
            msg='Image folder path is missing', headless=headless_bool
        )
        return

    if not os.path.exists(train_data_dir):
        output_message(
            msg='Image folder does not exist', headless=headless_bool
        )
        return

    if reg_data_dir != '':
        if not os.path.exists(reg_data_dir):
            output_message(
                msg='Regularisation folder does not exist',
                headless=headless_bool,
            )
            return

    if output_dir == '':
        output_message(
            msg='Output folder path is missing', headless=headless_bool
        )
        return

    if int(bucket_reso_steps) < 1:
        output_message(
            msg='Bucket resolution steps need to be greater than 0',
            headless=headless_bool,
        )
        return

    if noise_offset == '':
        noise_offset = 0

    if float(noise_offset) > 1 or float(noise_offset) < 0:
        output_message(
            msg='Noise offset need to be a value between 0 and 1',
            headless=headless_bool,
        )
        return

    # if float(noise_offset) > 0 and (
    #     multires_noise_iterations > 0 or multires_noise_discount > 0
    # ):
    #     output_message(
    #         msg="noise offset and multires_noise can't be set at the same time. Only use one or the other.",
    #         title='Error',
    #         headless=headless_bool,
    #     )
    #     return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if stop_text_encoder_training_pct > 0:
        output_message(
            msg='Output "stop text encoder training" is not yet supported. Ignoring',
            headless=headless_bool,
        )
        stop_text_encoder_training_pct = 0

    if check_if_model_exist(
        output_name, output_dir, save_model_as, headless=headless_bool
    ):
        return

    if optimizer == 'Adafactor' and lr_warmup != '0':
        output_message(
            msg="Warning: lr_scheduler is set to 'Adafactor', so 'LR warmup (% of steps)' will be considered 0.",
            title='Warning',
            headless=headless_bool,
        )
        lr_warmup = '0'

    # If string is empty set string to 0.
    if text_encoder_lr == '':
        text_encoder_lr = 0
    if unet_lr == '':
        unet_lr = 0

    # Get a list of all subfolders in train_data_dir
    subfolders = [
        f
        for f in os.listdir(train_data_dir)
        if os.path.isdir(os.path.join(train_data_dir, f))
    ]

    total_steps = 0

    # Loop through each subfolder and extract the number of repeats
    for folder in subfolders:
        try:
            # Extract the number of repeats from the folder name
            repeats = int(folder.split('_')[0])

            # Count the number of images in the folder
            num_images = len(
                [
                    f
                    for f, lower_f in (
                        (file, file.lower())
                        for file in os.listdir(
                            os.path.join(train_data_dir, folder)
                        )
                    )
                    if lower_f.endswith(('.jpg', '.jpeg', '.png', '.webp'))
                ]
            )

            log.info(f'Folder {folder}: {num_images} images found')

            # Calculate the total number of steps for this folder
            steps = repeats * num_images

            # log.info the result
            log.info(f'Folder {folder}: {steps} steps')

            total_steps += steps

        except ValueError:
            # Handle the case where the folder name does not contain an underscore
            log.info(
                f"Error: '{folder}' does not contain an underscore, skipping..."
            )

    if reg_data_dir == '':
        reg_factor = 1
    else:
        log.info(
            '\033[94mRegularisation images are used... Will double the number of steps required...\033[0m'
        )
        reg_factor = 2

    log.info(f'Total steps: {total_steps}')
    log.info(f'Train batch size: {train_batch_size}')
    log.info(f'Gradient accumulation steps: {gradient_accumulation_steps}')
    log.info(f'Epoch: {epoch}')
    log.info(f'Regulatization factor: {reg_factor}')

    # calculate max_train_steps
    max_train_steps = int(
        math.ceil(
            float(total_steps)
            / int(train_batch_size)
            / int(gradient_accumulation_steps)
            * int(epoch)
            * int(reg_factor)
        )
    )
    log.info(
        f'max_train_steps ({total_steps} / {train_batch_size} / {gradient_accumulation_steps} * {epoch} * {reg_factor}) = {max_train_steps}'
    )

    # calculate stop encoder training
    if stop_text_encoder_training_pct == None:
        stop_text_encoder_training = 0
    else:
        stop_text_encoder_training = math.ceil(
            float(max_train_steps) / 100 * int(stop_text_encoder_training_pct)
        )
    log.info(f'stop_text_encoder_training = {stop_text_encoder_training}')

    lr_warmup_steps = round(float(int(lr_warmup) * int(max_train_steps) / 100))
    log.info(f'lr_warmup_steps = {lr_warmup_steps}')

    run_cmd = f'accelerate launch --num_cpu_threads_per_process={num_cpu_threads_per_process} "train_network.py"'

    if v2:
        run_cmd += ' --v2'
    if v_parameterization:
        run_cmd += ' --v_parameterization'
    if enable_bucket:
        run_cmd += ' --enable_bucket'
    if no_token_padding:
        run_cmd += ' --no_token_padding'
    if weighted_captions:
        run_cmd += ' --weighted_captions'
    run_cmd += (
        f' --pretrained_model_name_or_path="{pretrained_model_name_or_path}"'
    )
    run_cmd += f' --train_data_dir="{train_data_dir}"'
    if len(reg_data_dir):
        run_cmd += f' --reg_data_dir="{reg_data_dir}"'
    run_cmd += f' --resolution={max_resolution}'
    run_cmd += f' --output_dir="{output_dir}"'
    if not logging_dir == '':
        run_cmd += f' --logging_dir="{logging_dir}"'
    run_cmd += f' --network_alpha="{network_alpha}"'
    if not training_comment == '':
        run_cmd += f' --training_comment="{training_comment}"'
    if not stop_text_encoder_training == 0:
        run_cmd += (
            f' --stop_text_encoder_training={stop_text_encoder_training}'
        )
    if not save_model_as == 'same as source model':
        run_cmd += f' --save_model_as={save_model_as}'
    if not float(prior_loss_weight) == 1.0:
        run_cmd += f' --prior_loss_weight={prior_loss_weight}'

    if LoRA_type == 'LoCon' or LoRA_type == 'LyCORIS/LoCon':
        try:
            import lycoris
        except ModuleNotFoundError:
            log.info(
                "\033[1;31mError:\033[0m The required module 'lycoris_lora' is not installed. Please install by running \033[33mupgrade.ps1\033[0m before running this program."
            )
            return
        run_cmd += f' --network_module=lycoris.kohya'
        run_cmd += f' --network_args "conv_dim={conv_dim}" "conv_alpha={conv_alpha}" "algo=lora"'

    if LoRA_type == 'LyCORIS/LoHa':
        try:
            import lycoris
        except ModuleNotFoundError:
            log.info(
                "\033[1;31mError:\033[0m The required module 'lycoris_lora' is not installed. Please install by running \033[33mupgrade.ps1\033[0m before running this program."
            )
            return
        run_cmd += f' --network_module=lycoris.kohya'
        run_cmd += f' --network_args "conv_dim={conv_dim}" "conv_alpha={conv_alpha}" "algo=loha"'
        # This is a hack to fix a train_network LoHA logic issue
        if not network_dropout > 0.0:
            run_cmd += f' --network_dropout="{network_dropout}"'

    if LoRA_type in ['Kohya LoCon', 'Standard']:
        kohya_lora_var_list = [
            'down_lr_weight',
            'mid_lr_weight',
            'up_lr_weight',
            'block_lr_zero_threshold',
            'block_dims',
            'block_alphas',
            'conv_dims',
            'conv_alphas',
            'rank_dropout',
            'module_dropout',
        ]

        run_cmd += f' --network_module=networks.lora'
        kohya_lora_vars = {
            key: value
            for key, value in vars().items()
            if key in kohya_lora_var_list and value
        }

        network_args = ''
        if LoRA_type == 'Kohya LoCon':
            network_args += f' conv_dim="{conv_dim}" conv_alpha="{conv_alpha}"'

        for key, value in kohya_lora_vars.items():
            if value:
                network_args += f' {key}="{value}"'

        if network_args:
            run_cmd += f' --network_args{network_args}'

    if LoRA_type in ['Kohya DyLoRA']:
        kohya_lora_var_list = [
            'conv_dim',
            'conv_alpha',
            'down_lr_weight',
            'mid_lr_weight',
            'up_lr_weight',
            'block_lr_zero_threshold',
            'block_dims',
            'block_alphas',
            'conv_dims',
            'conv_alphas',
            'rank_dropout',
            'module_dropout',
            'unit',
        ]

        run_cmd += f' --network_module=networks.dylora'
        kohya_lora_vars = {
            key: value
            for key, value in vars().items()
            if key in kohya_lora_var_list and value
        }

        network_args = ''

        for key, value in kohya_lora_vars.items():
            if value:
                network_args += f' {key}="{value}"'

        if network_args:
            run_cmd += f' --network_args{network_args}'

    if not (float(text_encoder_lr) == 0) or not (float(unet_lr) == 0):
        if not (float(text_encoder_lr) == 0) and not (float(unet_lr) == 0):
            run_cmd += f' --text_encoder_lr={text_encoder_lr}'
            run_cmd += f' --unet_lr={unet_lr}'
        elif not (float(text_encoder_lr) == 0):
            run_cmd += f' --text_encoder_lr={text_encoder_lr}'
            run_cmd += f' --network_train_text_encoder_only'
        else:
            run_cmd += f' --unet_lr={unet_lr}'
            run_cmd += f' --network_train_unet_only'
    else:
        if float(learning_rate) == 0:
            output_message(
                msg='Please input learning rate values.',
                headless=headless_bool,
            )
            return

    run_cmd += f' --network_dim={network_dim}'

    if LoRA_type not in ['LyCORIS/LoCon', 'LyCORIS/LoHa']:
        if not lora_network_weights == '':
            run_cmd += f' --network_weights="{lora_network_weights}"'
        if dim_from_weights:
            run_cmd += f' --dim_from_weights'

    if int(gradient_accumulation_steps) > 1:
        run_cmd += f' --gradient_accumulation_steps={int(gradient_accumulation_steps)}'
    if not output_name == '':
        run_cmd += f' --output_name="{output_name}"'
    if not lr_scheduler_num_cycles == '':
        run_cmd += f' --lr_scheduler_num_cycles="{lr_scheduler_num_cycles}"'
    else:
        run_cmd += f' --lr_scheduler_num_cycles="{epoch}"'
    if not lr_scheduler_power == '':
        run_cmd += f' --lr_scheduler_power="{lr_scheduler_power}"'

    if scale_weight_norms > 0.0:
        run_cmd += f' --scale_weight_norms="{scale_weight_norms}"'

    if network_dropout > 0.0:
        run_cmd += f' --network_dropout="{network_dropout}"'

    run_cmd += run_cmd_training(
        learning_rate=learning_rate,
        lr_scheduler=lr_scheduler,
        lr_warmup_steps=lr_warmup_steps,
        train_batch_size=train_batch_size,
        max_train_steps=max_train_steps,
        save_every_n_epochs=save_every_n_epochs,
        mixed_precision=mixed_precision,
        save_precision=save_precision,
        seed=seed,
        caption_extension=caption_extension,
        cache_latents=cache_latents,
        cache_latents_to_disk=cache_latents_to_disk,
        optimizer=optimizer,
        optimizer_args=optimizer_args,
    )

    run_cmd += run_cmd_advanced_training(
        max_train_epochs=max_train_epochs,
        max_data_loader_n_workers=max_data_loader_n_workers,
        max_token_length=max_token_length,
        resume=resume,
        save_state=save_state,
        mem_eff_attn=mem_eff_attn,
        clip_skip=clip_skip,
        flip_aug=flip_aug,
        color_aug=color_aug,
        shuffle_caption=shuffle_caption,
        gradient_checkpointing=gradient_checkpointing,
        full_fp16=full_fp16,
        xformers=xformers,
        # use_8bit_adam=use_8bit_adam,
        keep_tokens=keep_tokens,
        persistent_data_loader_workers=persistent_data_loader_workers,
        bucket_no_upscale=bucket_no_upscale,
        random_crop=random_crop,
        bucket_reso_steps=bucket_reso_steps,
        caption_dropout_every_n_epochs=caption_dropout_every_n_epochs,
        caption_dropout_rate=caption_dropout_rate,
        noise_offset_type=noise_offset_type,
        noise_offset=noise_offset,
        adaptive_noise_scale=adaptive_noise_scale,
        multires_noise_iterations=multires_noise_iterations,
        multires_noise_discount=multires_noise_discount,
        additional_parameters=additional_parameters,
        vae_batch_size=vae_batch_size,
        min_snr_gamma=min_snr_gamma,
        save_every_n_steps=save_every_n_steps,
        save_last_n_steps=save_last_n_steps,
        save_last_n_steps_state=save_last_n_steps_state,
        use_wandb=use_wandb,
        wandb_api_key=wandb_api_key,
        scale_v_pred_loss_like_noise_pred=scale_v_pred_loss_like_noise_pred,
    )

    run_cmd += run_cmd_sample(
        sample_every_n_steps,
        sample_every_n_epochs,
        sample_sampler,
        sample_prompts,
        output_dir,
    )

    # if not down_lr_weight == '':
    #     run_cmd += f' --down_lr_weight="{down_lr_weight}"'
    # if not mid_lr_weight == '':
    #     run_cmd += f' --mid_lr_weight="{mid_lr_weight}"'
    # if not up_lr_weight == '':
    #     run_cmd += f' --up_lr_weight="{up_lr_weight}"'
    # if not block_lr_zero_threshold == '':
    #     run_cmd += f' --block_lr_zero_threshold="{block_lr_zero_threshold}"'
    # if not block_dims == '':
    #     run_cmd += f' --block_dims="{block_dims}"'
    # if not block_alphas == '':
    #     run_cmd += f' --block_alphas="{block_alphas}"'
    # if not conv_dims == '':
    #     run_cmd += f' --conv_dims="{conv_dims}"'
    # if not conv_alphas == '':
    #     run_cmd += f' --conv_alphas="{conv_alphas}"'

    if print_only_bool:
        log.warning(
            'Here is the trainer command as a reference. It will not be executed:\n'
        )
        log.info(run_cmd)
    else:
        log.info(run_cmd)
        # Run the command
        if os.name == 'posix':
            os.system(run_cmd)
        else:
            subprocess.run(run_cmd)

        # check if output_dir/last is a folder... therefore it is a diffuser model
        last_dir = pathlib.Path(f'{output_dir}/{output_name}')

        if not last_dir.is_dir():
            # Copy inference model for v2 if required
            save_inference_file(
                output_dir, v2, v_parameterization, output_name
            )


def lora_tab(
    train_data_dir_input=gr.Textbox(),
    reg_data_dir_input=gr.Textbox(),
    output_dir_input=gr.Textbox(),
    logging_dir_input=gr.Textbox(),
    headless=False,
):
    dummy_db_true = gr.Label(value=True, visible=False)
    dummy_db_false = gr.Label(value=False, visible=False)
    dummy_headless = gr.Label(value=headless, visible=False)

    gr.Markdown(
        'Train a custom model using kohya train network LoRA python code...'
    )
    (
        button_open_config,
        button_save_config,
        button_save_as_config,
        config_file_name,
        button_load_config,
    ) = gradio_config(headless=headless)

    (
        pretrained_model_name_or_path,
        v2,
        v_parameterization,
        save_model_as,
        model_list,
    ) = gradio_source_model(
        save_model_as_choices=[
            'ckpt',
            'safetensors',
        ],
        headless=headless,
    )

    with gr.Tab('Folders'):
        with gr.Row():
            train_data_dir = gr.Textbox(
                label='Image folder',
                placeholder='Folder where the training folders containing the images are located',
            )
            train_data_dir_folder = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )
            train_data_dir_folder.click(
                get_folder_path,
                outputs=train_data_dir,
                show_progress=False,
            )
            reg_data_dir = gr.Textbox(
                label='Regularisation folder',
                placeholder='(Optional) Folder where where the regularization folders containing the images are located',
            )
            reg_data_dir_folder = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )
            reg_data_dir_folder.click(
                get_folder_path,
                outputs=reg_data_dir,
                show_progress=False,
            )
        with gr.Row():
            output_dir = gr.Textbox(
                label='Output folder',
                placeholder='Folder to output trained model',
            )
            output_dir_folder = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )
            output_dir_folder.click(
                get_folder_path,
                outputs=output_dir,
                show_progress=False,
            )
            logging_dir = gr.Textbox(
                label='Logging folder',
                placeholder='Optional: enable logging and output TensorBoard log to this folder',
            )
            logging_dir_folder = gr.Button(
                '📂', elem_id='open_folder_small', visible=(not headless)
            )
            logging_dir_folder.click(
                get_folder_path,
                outputs=logging_dir,
                show_progress=False,
            )
        with gr.Row():
            output_name = gr.Textbox(
                label='Model output name',
                placeholder='(Name of the model to output)',
                value='last',
                interactive=True,
            )
            training_comment = gr.Textbox(
                label='Training comment',
                placeholder='(Optional) Add training comment to be included in metadata',
                interactive=True,
            )
        train_data_dir.change(
            remove_doublequote,
            inputs=[train_data_dir],
            outputs=[train_data_dir],
        )
        reg_data_dir.change(
            remove_doublequote,
            inputs=[reg_data_dir],
            outputs=[reg_data_dir],
        )
        output_dir.change(
            remove_doublequote,
            inputs=[output_dir],
            outputs=[output_dir],
        )
        logging_dir.change(
            remove_doublequote,
            inputs=[logging_dir],
            outputs=[logging_dir],
        )
    with gr.Tab('Training parameters'):
        with gr.Row():
            LoRA_type = gr.Dropdown(
                label='LoRA type',
                choices=[
                    'Kohya DyLoRA',
                    'Kohya LoCon',
                    # 'LoCon',
                    'LyCORIS/LoCon',
                    'LyCORIS/LoHa',
                    'Standard',
                ],
                value='Standard',
            )
            with gr.Box():
                with gr.Row():
                    lora_network_weights = gr.Textbox(
                        label='LoRA network weights',
                        placeholder='(Optional)',
                        info='Path to an existing LoRA network weights to resume training from',
                    )
                    lora_network_weights_file = gr.Button(
                        document_symbol,
                        elem_id='open_folder_small',
                        visible=(not headless),
                    )
                    lora_network_weights_file.click(
                        get_any_file_path,
                        inputs=[lora_network_weights],
                        outputs=lora_network_weights,
                        show_progress=False,
                    )
                    dim_from_weights = gr.Checkbox(
                        label='DIM from weights',
                        value=False,
                        info='Automatically determine the dim(rank) from the weight file.',
                    )
        (
            learning_rate,
            lr_scheduler,
            lr_warmup,
            train_batch_size,
            epoch,
            save_every_n_epochs,
            mixed_precision,
            save_precision,
            num_cpu_threads_per_process,
            seed,
            caption_extension,
            cache_latents,
            cache_latents_to_disk,
            optimizer,
            optimizer_args,
        ) = gradio_training(
            learning_rate_value='0.0001',
            lr_scheduler_value='cosine',
            lr_warmup_value='10',
        )

        with gr.Row():
            text_encoder_lr = gr.Number(
                label='Text Encoder learning rate',
                value='5e-5',
                info='Optional',
            )
            unet_lr = gr.Number(
                label='Unet learning rate',
                value='0.0001',
                info='Optional',
            )
            network_dim = gr.Slider(
                minimum=1,
                maximum=1024,
                label='Network Rank (Dimension)',
                value=8,
                step=1,
                interactive=True,
            )
            network_alpha = gr.Slider(
                minimum=0.1,
                maximum=1024,
                label='Network Alpha',
                value=1,
                step=0.1,
                interactive=True,
                info='alpha for LoRA weight scaling',
            )
        with gr.Row(visible=False) as LoCon_row:

            # locon= gr.Checkbox(label='Train a LoCon instead of a general LoRA (does not support v2 base models) (may not be able to some utilities now)', value=False)
            conv_dim = gr.Slider(
                minimum=1,
                maximum=512,
                value=1,
                step=1,
                label='Convolution Rank (Dimension)',
            )
            conv_alpha = gr.Slider(
                minimum=0.1,
                maximum=512,
                value=1,
                step=0.1,
                label='Convolution Alpha',
            )
        with gr.Row(visible=False) as kohya_dylora:
            unit = gr.Slider(
                minimum=1,
                maximum=64,
                label='DyLoRA Unit',
                value=1,
                step=1,
                interactive=True,
            )

        # Show of hide LoCon conv settings depending on LoRA type selection
        def update_LoRA_settings(LoRA_type):
            # Print a message when LoRA type is changed
            log.info('LoRA type changed...')

            # Determine if LoCon_row should be visible based on LoRA_type
            LoCon_row = LoRA_type in {
                'LoCon',
                'Kohya DyLoRA',
                'Kohya LoCon',
                'LyCORIS/LoHa',
                'LyCORIS/LoCon',
            }

            # Determine if LoRA_type_change should be visible based on LoRA_type
            LoRA_type_change = LoRA_type in {
                'Standard',
                'Kohya DyLoRA',
                'Kohya LoCon',
            }

            # Determine if LoRA network weights should be visible based on LoRA_type
            LoRA_network_weights_visible = LoRA_type in {
                'Standard',
                'LoCon',
                'Kohya DyLoRA',
                'Kohya LoCon',
            }

            # Determine if kohya_dylora_visible should be visible based on LoRA_type
            kohya_dylora_visible = LoRA_type == 'Kohya DyLoRA'

            # Return the updated visibility settings for the groups
            return (
                gr.Group.update(visible=LoCon_row),
                gr.Group.update(visible=LoRA_type_change),
                gr.Group.update(visible=kohya_dylora_visible),
                gr.Textbox.update(visible=LoRA_network_weights_visible),
                gr.Button.update(visible=LoRA_network_weights_visible),
                gr.Checkbox.update(visible=LoRA_network_weights_visible),
            )

        with gr.Row():
            max_resolution = gr.Textbox(
                label='Max resolution',
                value='512,512',
                placeholder='512,512',
                info='The maximum resolution of dataset images. W,H',
            )
            stop_text_encoder_training = gr.Slider(
                minimum=0,
                maximum=100,
                value=0,
                step=1,
                label='Stop text encoder training',
                info='After what % of steps should the text encoder stop being trained. 0 = train for all steps.',
            )
            enable_bucket = gr.Checkbox(
                label='Enable buckets',
                value=True,
                info='Allow non similar resolution dataset images to be trained on.',
            )

        with gr.Accordion('Advanced Configuration', open=False):
            with gr.Row(visible=True) as kohya_advanced_lora:
                with gr.Tab(label='Weights'):
                    with gr.Row(visible=True):
                        down_lr_weight = gr.Textbox(
                            label='Down LR weights',
                            placeholder='(Optional) eg: 0,0,0,0,0,0,1,1,1,1,1,1',
                            info='Specify the learning rate weight of the down blocks of U-Net.',
                        )
                        mid_lr_weight = gr.Textbox(
                            label='Mid LR weights',
                            placeholder='(Optional) eg: 0.5',
                            info='Specify the learning rate weight of the mid block of U-Net.',
                        )
                        up_lr_weight = gr.Textbox(
                            label='Up LR weights',
                            placeholder='(Optional) eg: 0,0,0,0,0,0,1,1,1,1,1,1',
                            info='Specify the learning rate weight of the up blocks of U-Net. The same as down_lr_weight.',
                        )
                        block_lr_zero_threshold = gr.Textbox(
                            label='Blocks LR zero threshold',
                            placeholder='(Optional) eg: 0.1',
                            info='If the weight is not more than this value, the LoRA module is not created. The default is 0.',
                        )
                with gr.Tab(label='Blocks'):
                    with gr.Row(visible=True):
                        block_dims = gr.Textbox(
                            label='Block dims',
                            placeholder='(Optional) eg: 2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2',
                            info='Specify the dim (rank) of each block. Specify 25 numbers.',
                        )
                        block_alphas = gr.Textbox(
                            label='Block alphas',
                            placeholder='(Optional) eg: 2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2',
                            info='Specify the alpha of each block. Specify 25 numbers as with block_dims. If omitted, the value of network_alpha is used.',
                        )
                with gr.Tab(label='Conv'):
                    with gr.Row(visible=True):
                        conv_dims = gr.Textbox(
                            label='Conv dims',
                            placeholder='(Optional) eg: 2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2',
                            info='Expand LoRA to Conv2d 3x3 and specify the dim (rank) of each block. Specify 25 numbers.',
                        )
                        conv_alphas = gr.Textbox(
                            label='Conv alphas',
                            placeholder='(Optional) eg: 2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2',
                            info='Specify the alpha of each block when expanding LoRA to Conv2d 3x3. Specify 25 numbers. If omitted, the value of conv_alpha is used.',
                        )
            with gr.Row():
                no_token_padding = gr.Checkbox(
                    label='No token padding', value=False
                )
                gradient_accumulation_steps = gr.Number(
                    label='Gradient accumulate steps', value='1'
                )
                weighted_captions = gr.Checkbox(
                    label='Weighted captions',
                    value=False,
                    info='Enable weighted captions in the standard style (token:1.3). No commas inside parens, or shuffle/dropout may break the decoder.',
                )
            with gr.Row():
                prior_loss_weight = gr.Number(
                    label='Prior loss weight', value=1.0
                )
                lr_scheduler_num_cycles = gr.Textbox(
                    label='LR number of cycles',
                    placeholder='(Optional) For Cosine with restart and polynomial only',
                )

                lr_scheduler_power = gr.Textbox(
                    label='LR power',
                    placeholder='(Optional) For Cosine with restart and polynomial only',
                )
            with gr.Row():
                scale_weight_norms = gr.Slider(
                    label='Scale weight norms',
                    value=0,
                    minimum=0,
                    maximum=1,
                    step=0.01,
                    info='Max Norm Regularization is a technique to stabilize network training by limiting the norm of network weights. It may be effective in suppressing overfitting of LoRA and improving stability when used with other LoRAs. See PR for details.',
                    interactive=True,
                )
                network_dropout = gr.Slider(
                    label='Network dropout',
                    value=0,
                    minimum=0,
                    maximum=1,
                    step=0.01,
                    info='Is a normal probability dropout at the neuron level. In the case of LoRA, it is applied to the output of down. Recommended range 0.1 to 0.5',
                )
                rank_dropout = gr.Slider(
                    label='Rank dropout',
                    value=0,
                    minimum=0,
                    maximum=1,
                    step=0.01,
                    info='can specify `rank_dropout` to dropout each rank with specified probability. Recommended range 0.1 to 0.3',
                )
                module_dropout = gr.Slider(
                    label='Module dropout',
                    value=0.0,
                    minimum=0.0,
                    maximum=1.0,
                    step=0.01,
                    info='can specify `module_dropout` to dropout each rank with specified probability. Recommended range 0.1 to 0.3',
                )
            (
                # use_8bit_adam,
                xformers,
                full_fp16,
                gradient_checkpointing,
                shuffle_caption,
                color_aug,
                flip_aug,
                clip_skip,
                mem_eff_attn,
                save_state,
                resume,
                max_token_length,
                max_train_epochs,
                max_data_loader_n_workers,
                keep_tokens,
                persistent_data_loader_workers,
                bucket_no_upscale,
                random_crop,
                bucket_reso_steps,
                caption_dropout_every_n_epochs,
                caption_dropout_rate,
                noise_offset_type,
                noise_offset,
                adaptive_noise_scale,
                multires_noise_iterations,
                multires_noise_discount,
                additional_parameters,
                vae_batch_size,
                min_snr_gamma,
                save_every_n_steps,
                save_last_n_steps,
                save_last_n_steps_state,
                use_wandb,
                wandb_api_key,
                scale_v_pred_loss_like_noise_pred,
            ) = gradio_advanced_training(headless=headless)
            color_aug.change(
                color_aug_changed,
                inputs=[color_aug],
                outputs=[cache_latents],
            )

        (
            sample_every_n_steps,
            sample_every_n_epochs,
            sample_sampler,
            sample_prompts,
        ) = sample_gradio_config()

        LoRA_type.change(
            update_LoRA_settings,
            inputs=[LoRA_type],
            outputs=[
                LoCon_row,
                kohya_advanced_lora,
                kohya_dylora,
                lora_network_weights,
                lora_network_weights_file,
                dim_from_weights,
            ],
        )

    with gr.Tab('Tools'):
        gr.Markdown(
            'This section provide Dreambooth tools to help setup your dataset...'
        )
        gradio_dreambooth_folder_creation_tab(
            train_data_dir_input=train_data_dir,
            reg_data_dir_input=reg_data_dir,
            output_dir_input=output_dir,
            logging_dir_input=logging_dir,
            headless=headless,
        )
        gradio_dataset_balancing_tab(headless=headless)
        gradio_merge_lora_tab(headless=headless)
        gradio_svd_merge_lora_tab(headless=headless)
        gradio_resize_lora_tab(headless=headless)
        gradio_verify_lora_tab(headless=headless)

    button_run = gr.Button('Train model', variant='primary')

    button_print = gr.Button('Print training command')

    # Setup gradio tensorboard buttons
    button_start_tensorboard, button_stop_tensorboard = gradio_tensorboard()

    button_start_tensorboard.click(
        start_tensorboard,
        inputs=logging_dir,
        show_progress=False,
    )

    button_stop_tensorboard.click(
        stop_tensorboard,
        show_progress=False,
    )

    settings_list = [
        pretrained_model_name_or_path,
        v2,
        v_parameterization,
        logging_dir,
        train_data_dir,
        reg_data_dir,
        output_dir,
        max_resolution,
        learning_rate,
        lr_scheduler,
        lr_warmup,
        train_batch_size,
        epoch,
        save_every_n_epochs,
        mixed_precision,
        save_precision,
        seed,
        num_cpu_threads_per_process,
        cache_latents,
        cache_latents_to_disk,
        caption_extension,
        enable_bucket,
        gradient_checkpointing,
        full_fp16,
        no_token_padding,
        stop_text_encoder_training,
        # use_8bit_adam,
        xformers,
        save_model_as,
        shuffle_caption,
        save_state,
        resume,
        prior_loss_weight,
        text_encoder_lr,
        unet_lr,
        network_dim,
        lora_network_weights,
        dim_from_weights,
        color_aug,
        flip_aug,
        clip_skip,
        gradient_accumulation_steps,
        mem_eff_attn,
        output_name,
        model_list,
        max_token_length,
        max_train_epochs,
        max_data_loader_n_workers,
        network_alpha,
        training_comment,
        keep_tokens,
        lr_scheduler_num_cycles,
        lr_scheduler_power,
        persistent_data_loader_workers,
        bucket_no_upscale,
        random_crop,
        bucket_reso_steps,
        caption_dropout_every_n_epochs,
        caption_dropout_rate,
        optimizer,
        optimizer_args,
        noise_offset_type,
        noise_offset,
        adaptive_noise_scale,
        multires_noise_iterations,
        multires_noise_discount,
        LoRA_type,
        conv_dim,
        conv_alpha,
        sample_every_n_steps,
        sample_every_n_epochs,
        sample_sampler,
        sample_prompts,
        additional_parameters,
        vae_batch_size,
        min_snr_gamma,
        down_lr_weight,
        mid_lr_weight,
        up_lr_weight,
        block_lr_zero_threshold,
        block_dims,
        block_alphas,
        conv_dims,
        conv_alphas,
        weighted_captions,
        unit,
        save_every_n_steps,
        save_last_n_steps,
        save_last_n_steps_state,
        use_wandb,
        wandb_api_key,
        scale_v_pred_loss_like_noise_pred,
        scale_weight_norms,
        network_dropout,
        rank_dropout,
        module_dropout,
    ]

    button_open_config.click(
        open_configuration,
        inputs=[dummy_db_true, config_file_name] + settings_list,
        outputs=[config_file_name] + settings_list + [LoCon_row],
        show_progress=False,
    )

    button_load_config.click(
        open_configuration,
        inputs=[dummy_db_false, config_file_name] + settings_list,
        outputs=[config_file_name] + settings_list + [LoCon_row],
        show_progress=False,
    )

    button_save_config.click(
        save_configuration,
        inputs=[dummy_db_false, config_file_name] + settings_list,
        outputs=[config_file_name],
        show_progress=False,
    )

    button_save_as_config.click(
        save_configuration,
        inputs=[dummy_db_true, config_file_name] + settings_list,
        outputs=[config_file_name],
        show_progress=False,
    )

    button_run.click(
        train_model,
        inputs=[dummy_headless] + [dummy_db_false] + settings_list,
        show_progress=False,
    )

    button_print.click(
        train_model,
        inputs=[dummy_headless] + [dummy_db_true] + settings_list,
        show_progress=False,
    )

    return (
        train_data_dir,
        reg_data_dir,
        output_dir,
        logging_dir,
    )


def UI(**kwargs):
    css = ''

    headless = kwargs.get('headless', False)
    log.info(f'headless: {headless}')

    if os.path.exists('./style.css'):
        with open(os.path.join('./style.css'), 'r', encoding='utf8') as file:
            log.info('Load CSS...')
            css += file.read() + '\n'

    interface = gr.Blocks(
        css=css, title='Kohya_ss GUI', theme=gr.themes.Default()
    )

    with interface:
        with gr.Tab('LoRA'):
            (
                train_data_dir_input,
                reg_data_dir_input,
                output_dir_input,
                logging_dir_input,
            ) = lora_tab(headless=headless)
        with gr.Tab('Utilities'):
            utilities_tab(
                train_data_dir_input=train_data_dir_input,
                reg_data_dir_input=reg_data_dir_input,
                output_dir_input=output_dir_input,
                logging_dir_input=logging_dir_input,
                enable_copy_info_button=True,
                headless=headless,
            )

    # Show the interface
    launch_kwargs = {}
    username = kwargs.get('username')
    password = kwargs.get('password')
    server_port = kwargs.get('server_port', 0)
    inbrowser = kwargs.get('inbrowser', False)
    share = kwargs.get('share', False)
    server_name = kwargs.get('listen')

    launch_kwargs['server_name'] = server_name
    if username and password:
        launch_kwargs['auth'] = (username, password)
    if server_port > 0:
        launch_kwargs['server_port'] = server_port
    if inbrowser:
        launch_kwargs['inbrowser'] = inbrowser
    if share:
        launch_kwargs['share'] = share
    log.info(launch_kwargs)
    interface.launch(**launch_kwargs)


if __name__ == '__main__':
    # torch.cuda.set_per_process_memory_fraction(0.48)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--listen',
        type=str,
        default='127.0.0.1',
        help='IP to listen on for connections to Gradio',
    )
    parser.add_argument(
        '--username', type=str, default='', help='Username for authentication'
    )
    parser.add_argument(
        '--password', type=str, default='', help='Password for authentication'
    )
    parser.add_argument(
        '--server_port',
        type=int,
        default=0,
        help='Port to run the server listener on',
    )
    parser.add_argument(
        '--inbrowser', action='store_true', help='Open in browser'
    )
    parser.add_argument(
        '--share', action='store_true', help='Share the gradio UI'
    )
    parser.add_argument(
        '--headless', action='store_true', help='Is the server headless'
    )

    args = parser.parse_args()

    UI(
        username=args.username,
        password=args.password,
        inbrowser=args.inbrowser,
        server_port=args.server_port,
        share=args.share,
        listen=args.listen,
        headless=args.headless,
    )
