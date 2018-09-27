import { NgModule } from '@angular/core';
import { MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, 
  MatSortModule, MatProgressSpinnerModule, MatFormFieldModule, MatInputModule, MatExpansionModule } from '@angular/material';

@NgModule({
  imports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, 
    MatProgressSpinnerModule, MatFormFieldModule, MatInputModule, MatExpansionModule],
  exports: [MatButtonModule, MatCheckboxModule, MatTableModule, MatPaginatorModule, MatSortModule, 
    MatProgressSpinnerModule, MatFormFieldModule, MatInputModule, MatExpansionModule],
})
export class MaterialModule { }