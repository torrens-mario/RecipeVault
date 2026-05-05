# RecipeVault 
Proyecto de la asignatura de Seguridad en la Nube. Proyecto basado en un recetario de cocina en el cual se podrá compartir con otros usuarios,es decir una aplicación que te ayude a la hora de cocinar, en la que puedas guardar recetas que tú quieras y las puedas compartir con otros usuarios, también puede ser de utilidad para cuando vayas a hacer la compra te diga que ingredientes necesitas según lo que quieras cocinar

Creadas varias políticas en Azure
- La primera para que se fuerce que todo lo que viaje desde y hacia el Blob Storage, que es donde se guardarán las fotos, viaje en HTTPS cifrado y no por HTTP sin protección
- La segunda, para que obligue a que todos los recursos tengan tags específicos a la hora de crearlos, para así poder saber que pertenece a RecipeVault, para poder auditar costos por poryecto y para poder identificar al responsable en caso de que haya pasado alguna cosa.