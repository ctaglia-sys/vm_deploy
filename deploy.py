
import sys
import os
import subprocess 
import uuid
import config as cfg
from inspect import currentframe, getframeinfo

DEBUG=False

def print_error(frameinfo, message=""):
  if not message:
    message = "ERROR"
  print("==========================================")
  print(message)
  
  print(frameinfo.filename, frameinfo.lineno)
  print("==========================================")

def set_dirs(image_path):
  """
   ----
  """
  command = ["mkdir", '-p', image_path]
  p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (out,err) = p.communicate() # TODO: chequear si dio ERROR

  print("- creado: %s" % image_path )
  return True

def snapshot_file(ro_image, snapshot_filename):
  """
   ----
  """
  # 1. chequear que no exista o borrar el snapshot
  # 2. chequear que exista ro image o descargarlo
  command = [
        "qemu-img", 
        "create", 
        "-f", 
        "qcow2", 
        "-b", 
        ro_image, 
        snapshot_filename
      ]

  p = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  (out,err) = p.communicate()

  if DEBUG:
    print(out)
    print(err)
  if not err:
    print("- creada: %s" % snapshot_filename)
  
  return True

def vm_xml_definition_filename(xml_definition_filename, vm_name, vm_image_path):
  command = ["virt-install", 
  "--connect", 
  "qemu:///system", 
  "--import", 
  "--name", 
  vm_name, 
  "--ram", 
  cfg.RAM, 
  "--vcpus", 
  cfg.VCPUS, 
  "--os-type=linux", 
  "--os-variant=virtio26", 
  "--disk", 
  "path=" + vm_image_path + '/' + vm_name + '.qcow2'",format=qcow2,bus=virtio", 
  "--vnc", 
  "--noautoconsole", 
  "--print-xml"]

  if DEBUG:
    print(command)

  p = subprocess.Popen(command,stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
  (out,err) = p.communicate()
  print(err)
  if err:
    frameinfo = getframeinfo(currentframe())
    print_error(frameinfo)
    raise Exception

  arr_xml = list(filter(lambda x: x!= '', out.split('\n')))
  # arr_xml[0] --> <domain type="kvm">', 
  # cambia por--> <domain type='kvm' xmlns:qemu='http://libvirt.org/schemas/domain/qemu/1.0'>
  arr_xml[0] = '<domain type="kvm" xmlns:qemu="http://libvirt.org/schemas/domain/qemu/1.0">'

  # # Elimino el cierre del xml </domain> para apendear el quemu:commandline al archivo
  del(arr_xml[len(arr_xml) -1])
  
  print("Imprimiendo en: %s" % xml_definition_filename)
  with open(vm_image_path + xml_definition_filename, 'w') as file:
    for linea in arr_xml:
      file.write(linea + '\n')
    
    vm_ignition_file_path = vm_image_path + vm_name + '.ign'
    ign = """
      <qemu:commandline>
        <qemu:arg value='-fw_cfg'/>
        <qemu:arg value='name=opt/org.flatcar-linux/config,file=""" + vm_ignition_file_path + """'/>
      </qemu:commandline>
    </domain>"""
    file.write(ign)
  file.close()

  return True

def set_ingition_file(ignition_definition_filename):

  # with open(xml_definition_filename, "r") as file:
  #   for line in file:
  #     if '<mac address=' in line:
  #       cfg.MACADDRESS=print(line.split('"')[1])

  ign_values = {
    "_hostname_": cfg.HOSTNAME,
    "_ipaddress_": cfg.IPADDRESS,
    "_gateway_": cfg.GATEWAY,
    "_dns_": cfg.DNS,
    "_username_": cfg.USERNAME,
    "_ssh-rsa_": cfg.SSHRSA
  }

  ign_values_keys = ign_values.keys()
  ign = open(ignition_definition_filename, "w")
  template = open("template.ign", "r").read()

  for k in ign_values.keys():
    template = template.replace(k,ign_values[k])

  ign.write(template)
  ign.close()
  return True

def define_vm(xml_definition_filename, vm_name):
  command_define = [
                  "virsh", 
                  "define",
                   xml_definition_filename]

  p = subprocess.Popen(command_define,stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, universal_newlines=True)
  (out,err) = p.communicate()

  if err:
    print(err)
    frameinfo = getframeinfo(currentframe())
    print_error(frameinfo)
    raise Exception
  print("%s definida" % vm_name)
  return True

def start_vm(vm_name):
  command_start_vm = [
                    "virsh",
                    "start",
                    vm_name]

  p = subprocess.Popen(command_start_vm,stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, universal_newlines=True)
  (out,err) = p.communicate()

  if err:
    print(err)
    frameinfo = getframeinfo(currentframe())
    print_error(frameinfo)
    raise Exception
  print("%s Arrancada" % vm_name)

if __name__ == '__main__':

  
  # Imagen RO con FlatCar
  ro_image = cfg.LIBVIRT_IMAGE_PATH + 'flatcar-linux/' + 'flatcar_production_qemu_image.img'
  snapshot_filename = cfg.VM_PATH + cfg.VM_NAME + '.qcow2'

  xml_definition_filename = cfg.VM_NAME + '.xml'
  ignition_definition_filename = cfg.VM_PATH + cfg.VM_NAME + '.ign'



  # ***************************************************************************

  # 1. crear directorios
  ret = set_dirs(cfg.VM_PATH)

  # 2. crear qcow2
  if ret:
    print("---------- vm dirs: ok ----------")
    ret = snapshot_file(ro_image, snapshot_filename)

  # # 3. crear xml
  if ret:
    print("---------- snapshot: ok ----------")
    # vm_xml_definition_filename(xml_definition_filename, vm_name, vm_image_path):
    ret = vm_xml_definition_filename(xml_definition_filename, cfg.VM_NAME, cfg.VM_PATH)

  # # 4. Ignition File
  if ret:
    print("---------- definition file: ok ----------")
    # set_ingition_file(ignition_definition_filename)
    ret = set_ingition_file(ignition_definition_filename)

  # # 5. define
  if ret:
    print("---------- ignition file: ok ----------")
    # define_vm(xml_definition_filename, vm_name)
    ret = define_vm(cfg.VM_PATH + cfg.VM_NAME + '.xml', cfg.VM_NAME)

  # # 6. start
  if ret:
    start_vm(cfg.VM_NAME)
    print("---------- %s started ----------" % cfg.VM_NAME)
  
